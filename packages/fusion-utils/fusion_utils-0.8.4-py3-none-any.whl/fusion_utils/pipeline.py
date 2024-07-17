import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google.cloud import bigquery
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
from .task import Task
from .errors import *
import time
import sys
import threading
import pandas as pd
import numpy as np
import re
import io
from .dual_logger import DualLogger


class Pipeline:
    def __init__(self, name, QA_flag=None):
        # Set up in-memory log
        self.dual_logger = DualLogger()

        if QA_flag is None:
            self.dual_logger.logger.info("NO QA_FLAG PASSED. DEFAULTING TO TRUE.")
            self.QA = True
        elif isinstance(QA_flag, str):
            self.QA = QA_flag.lower() == 'true'
        else:
            self.QA = QA_flag

        self.name = name
        self.stages = []
        self.errors = []
        self.halt_execution = False
        self.qa_queries = []
        self.tasks = []
        self.client = bigquery.Client(project='aic-production-core')
        self.temp_tables = {}
        self.status = {}
        self.set_table_map()
        self.initialize_datasets()
        self.set_smtp_ip()
        self.task_execution_times = {}


    def print_initial_summary(self):
        self.dual_logger.logger.info("\nInitial Pipeline Summary")
        self.dual_logger.logger.info("========================")
        self.dual_logger.logger.info(f"Pipeline Name: {self.name}")
        self.dual_logger.logger.info(f"QA Mode: {'Enabled' if self.QA else 'Disabled'}")
        self.dual_logger.logger.info(f"Total Tasks: {len(self.tasks)}")
        self.dual_logger.logger.info(f"Total Stages: {len(set(task.stage for task in self.tasks))}")
        self.dual_logger.logger.info("Tasks by Stage:")
        
        stages = {}
        for task in self.tasks:
            if task.stage not in stages:
                stages[task.stage] = []
            stages[task.stage].append(task)
        
        for stage, tasks in sorted(stages.items()):
            self.dual_logger.logger.info(f"  Stage {stage}:")
            for task in tasks:
                self.dual_logger.logger.info(f"    - {task.name}")


    def print_elapsed_time(self, start_time, stop_event):
        while not stop_event.is_set():
            elapsed_time = time.time() - start_time
            sys.stdout.write(f"\rElapsed time: {elapsed_time:.2f} seconds")
            sys.stdout.flush()
            time.sleep(5)

    def set_table_map(self, dataset='3349c7ea_09a2_461d_87f5_312a5401c51a', table='LKP_QA_TABLE_MAPPING'):
        table_map = f'`{dataset}.{table}`'
        self.table_map_df = self.client.query(f'SELECT * FROM {table_map}').to_dataframe()
        self.dataset_map = dict(zip(self.table_map_df['alias'], self.table_map_df['qa_dataset' if self.QA else 'prod_dataset']))

    def set_email_recipients(self, recipients):
        if isinstance(recipients, str):
            self.recipients = [recipients]
        else:
            self.recipients = recipients

    def set_smtp_ip(self, dataset='3349c7ea_09a2_461d_87f5_312a5401c51a', table='LKP_SMTP_IP'):
        if '_' not in dataset:
            dataset_id = self.translate_dataset(dataset)
            smtp_map = f'`{dataset_id}.{table}`'
        else:
            smtp_map = f'`{dataset}.{table}`'
        try:
            query = f"SELECT ip FROM {smtp_map} LIMIT 1"
            results = self.client.query(query).result()
            for row in results:
                self.smtp_ip = row['ip']
                break
            if not isinstance(self.smtp_ip, str):
                raise ValueError("Retrieved SMTP IP is not a string.")
        except Exception as e:
            raise ValueError('Cannot retrieve SMTP server IP.') from e

    def translate_dataset(self, alias):
        return getattr(self, alias)

    def initialize_datasets(self):
        for _, row in self.table_map_df.iterrows():
            alias = row['alias']
            dataset = row['qa_dataset'] if self.QA else row['prod_dataset']
            setattr(self, alias, dataset)

    def translate_tables(self, query):
        for alias, dataset_id in self.dataset_map.items():
            query = query.replace(f'${alias}:', f'{dataset_id}.')
        return query

    def translate_query(self, query):
        try:
            query = self.translate_tables(query)
            for alias, table_name in self.temp_tables.items():
                query = query.replace(f'${{{alias}}}', table_name)
            if re.search(r'\$\{.+?\}', query):
                raise TaskError("No matching task alias/temp table found for the string attempted to be translated within the query.")
            return query
        except KeyError as e:
            raise TaskError(f"Failed to translate query: Missing key {str(e)} in temp tables")

    def send_email(self, subject, body, recipients=None):
        if not hasattr(self, 'smtp_ip'):
            raise SMTPConfigurationError("SMTP server IP is not configured.")

        if not recipients:
            if hasattr(self, 'recipients'):
                recipients = self.recipients
            else:
                raise SMTPConfigurationError('No recipient passed or defined within pipeline attributes.')

        if isinstance(recipients, str):
            recipients = [recipients]

        sender = 'pinapps@jdpa.com'
        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = ", ".join(recipients)
        message['Subject'] = subject
        css = '<style>.pass { color: #008000; } .fail { color: #FF0000; }</style>'
        body_html = f"<html><head>{css}</head><body>{body}</body></html>"
        message.attach(MIMEText(body_html, 'html'))
        
        # Attach the log file to the email
        self.dual_logger.attach_to_email(message)

        try:
            server = smtplib.SMTP(self.smtp_ip, 25)
            server.ehlo()
            server.sendmail(sender, recipients, message.as_string())
            server.quit()
            self.dual_logger.logger.info("Email sent successfully.")
        except Exception as e:
            self.dual_logger.logger.info("Failed to send email:", str(e))



    def execute_query(self, query, temp_table_name=None):
        try:
            query = self.translate_query(query)
            start_time = time.time()
            stop_event = threading.Event()
            elapsed_time_thread = threading.Thread(target=self.print_elapsed_time, args=(start_time, stop_event))
            elapsed_time_thread.start()

            ddl_patterns = [
                r"create\s+table", r"execute\s", r"replace\s+table", r"insert\s+into", r"drop\s+table",
                r"alter\s+table", r"truncate\s+table", r"\bupdate\b", r"delete\s+from"
            ]

            is_ddl = any(re.search(pattern, query.lower()) for pattern in ddl_patterns)

            if temp_table_name and not is_ddl:
                job_config = bigquery.QueryJobConfig(
                    destination=temp_table_name,
                    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
                )
                query_job = self.client.query(query, job_config=job_config)
            else:
                query_job = self.client.query(query)

            query_job.result()

            stop_event.set()
            elapsed_time_thread.join()

            end_time = time.time()
            total_elapsed_time = end_time - start_time
            self.dual_logger.logger.info(f"\nQuery executed in {total_elapsed_time:.2f} seconds.")

            if not is_ddl:
                self.create_temp_table(query_job, temp_table_name)
                self.update_temp_table_list(query, temp_table_name)

            return query_job, total_elapsed_time

        except TaskError as e:
            stop_event.set()
            elapsed_time_thread.join()
            self.dual_logger.logger.error(f"TaskError: {e}")
            raise e
        except Exception as e:
            stop_event.set()
            elapsed_time_thread.join()
            error_message = str(e).split('\n\n')[0].strip()
            self.dual_logger.logger.error(f"Failed to execute query: {error_message}")
            raise TaskError(f"Failed to execute query: {error_message}")



    def create_temp_table(self, query_job, temp_table_name):
        try:
            destination = query_job.destination
            if destination is None:
                self.dual_logger.logger.info(f"No destination table created for job: {query_job.job_id}")
                return None

            table = self.client.get_table(destination)
            if table.table_type != 'TEMPORARY':
                table.expires = datetime.datetime.now() + datetime.timedelta(hours=1)
                self.client.update_table(table, ["expires"])
                self.dual_logger.logger.info(f"Temporary table {temp_table_name} created.")
            else:
                self.dual_logger.logger.info(f"Skipping expiration update for anonymous table {destination}")
            return temp_table_name
        except Exception as e:
            error_message = str(e).split('\n\n')[0].strip()
            raise TaskError(f"Failed to create temporary table {temp_table_name}: {error_message}")


    def log_task_execution(self, task_name, data_size, elapsed_time):
        try:
            if "test" in task_name.lower():
                self.dual_logger.logger.info(f"Skipping logging for test task: {task_name}")
                return

            log_query = f"""
            INSERT INTO `{self.translate_dataset('Silver')}.LKP_TASK_LOG` (task_name, data_size, date_run, elapsed_time)
            VALUES ('{task_name}', {data_size}, '{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}', {elapsed_time})
            """
            self.client.query(log_query).result()
            self.dual_logger.logger.info(f"Logged task execution for task: {task_name}")
        except Exception as e:
            self.dual_logger.logger.error(f"Failed to log task execution for task: {task_name}. Error: {str(e)}")

    def add_task(self, task):
        self.tasks.append(task)
        if task.is_qa:
            temp_table = None
        else:
            temp_table = f"{self.client.project}.AIC_BRANCH_JOB.{task.table_alias}"
        task.temp_table = temp_table


    def add_external_task(self, df: pd.DataFrame, temp_table_name: str):
        """
        Add an external task to load a DataFrame to a temporary table in BigQuery and update the temp table list.
        
        Args:
            df (pd.DataFrame): The DataFrame to load.
            temp_table_name (str): The name of the temporary table.
        """
        dataset_id = "AIC_BRANCH_JOB"
        table_ref = f"{self.client.project}.{dataset_id}.{temp_table_name}"
        
        # Define the load job configuration
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )
        
        # Load the DataFrame to BigQuery
        load_job = self.client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        load_job.result()  # Wait for the job to complete

        # Simulate the query job object
        query_job = type('QueryJob', (object,), {'destination': table_ref})
        
        # Use the existing create_temp_table method to set expiration and update the temp table list
        self.create_temp_table(query_job, temp_table_name)
        self.temp_tables[temp_table_name] = table_ref  # Update the temp_tables dictionary



    def execute_stage(self, stage_tasks):
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.execute_task, task): task for task in stage_tasks}
            for future in as_completed(futures):
                task = futures[future]
                try:
                    future.result()
                except Exception as e:
                    error_message = f"Task '{task.name}' in stage {task.stage} failed with exception: {e}"
                    self.errors.append(error_message)
                    print(error_message)
                    if not task.optional:
                        self.halt_execution = True
                        return

    def execute_all(self):
        self.print_initial_summary()
        try:
            max_stage = max(task.stage for task in self.tasks)
            stages_executed = set()
            
            # Execute regular tasks stage by stage
            for stage in range(1, max_stage + 1):
                if self.halt_execution:
                    break
                stage_tasks = [task for task in self.tasks if task.stage == stage]
                if stage_tasks and stage not in stages_executed:
                    self.dual_logger.logger.info(f"Executing stage {stage} with {len(stage_tasks)} task(s).")
                    self.execute_stage(stage_tasks)
                    stages_executed.add(stage)

            # Check for errors in regular tasks before executing QA tasks
            if not self.errors and not self.halt_execution:
                qa_tasks = [task for task in self.tasks if task.stage == Task.QA_STAGE]
                if qa_tasks and Task.QA_STAGE not in stages_executed:
                    self.dual_logger.logger.info(f"Executing stage {Task.QA_STAGE} with {len(qa_tasks)} task(s).")
                    self.execute_stage(qa_tasks)
                    stages_executed.add(Task.QA_STAGE)
            else:
                self.dual_logger.logger.info("Skipping QA tasks due to errors in regular tasks.")

            self.dual_logger.logger.info("Pipeline execution completed.")
        except Exception as e:
            error_message = f"Pipeline Failure: {e}"
            self.errors.append(error_message)
            self.dual_logger.logger.error(error_message)
        finally:
            if self.errors:
                self.dual_logger.logger.info("Errors encountered during pipeline execution:")
                for error in self.errors:
                    self.dual_logger.logger.info(error)
            self.send_completion_email()


    def execute_task(self, task):
        start_time = time.time()
        if task.is_qa:
            self.execute_qa_task(task)
        else:
            self.execute_regular_task(task)
        end_time = time.time()
        self.task_execution_times[task.name] = end_time - start_time

    def execute_regular_task(self, task):
        try:
            if task not in self.tasks:
                raise TaskError(f"Task '{task.name}' has not been added to the pipeline. Use Pipeline.add_task() to execute.")

            if not task.query_definition:
                if not task.optional:
                    raise TaskError(f'{task.name} does not have a defined query')
                else:
                    self.dual_logger.logger.warning(f'WARNING: {task.name} does not have a defined query. Skipping optional task...')
                    self.update_status(task, 'Failed: No query defined')
                    return

            self.update_status(task, 'Started')

            try:
                task.query = self.translate_query(task.query_definition)
            except TaskError as e:
                self.dual_logger.logger.error(f"Failed to translate query for task '{task.name}': {e}")
                raise

            estimated_data_size = self.estimate_data_size(task.query)
            self.dual_logger.logger.info(f"Estimated data size for task '{task.name}': {estimated_data_size/1000000000:.2f} Gb")

            estimated_run_time = self.estimate_run_time(estimated_data_size, task.name)
            if estimated_run_time:
                self.dual_logger.logger.info(f"Estimated run time for task '{task.name}': {estimated_run_time:.2f} seconds")

            try:
                temp_table_name = f"{self.client.project}.AIC_BRANCH_JOB.{task.table_alias}"
                query_job, elapsed_time = self.execute_query(task.query, temp_table_name)
                self.update_temp_table_list(task.name, temp_table_name)
                self.log_task_execution(task.name, estimated_data_size, elapsed_time)
                self.update_status(task, 'Completed')
                self.dual_logger.logger.info(f"{task.name} Completed.")
            except Exception as e:
                self.update_status(task, f'Failed: {str(e)}')
                if not task.optional:
                    raise e

        except Exception as e:
            error_message = f"Task '{task.name}' in stage {task.stage} failed with exception: {e}"
            self.errors.append(error_message)
            self.dual_logger.logger.error(error_message)
            self.update_status(task, f"Failed with exception: {str(e)}")
            if not task.optional:
                self.halt_execution = True



    def execute_qa_task(self, task):
        self.dual_logger.logger.info(f"Executing QA task '{task.name}'")
        try:
            query = self.translate_query(task.query_definition)
            query_job = self.client.query(query)
            result = query_job.result().to_dataframe()

            if not callable(task.condition):
                raise TaskError(f"Condition for task '{task.name}' is not callable")

            condition_result = task.condition(result)

            if condition_result:
                self.dual_logger.logger.info(f"QA check passed for task '{task.name}'")
                self.update_status(task, 'Completed')
            else:
                self.dual_logger.logger.info(f"QA check failed for task '{task.name}'")
                if task.optional:
                    self.update_status(task, 'Failed (Optional): QA check did not pass')
                else:
                    self.update_status(task, 'Failed: QA check did not pass')

            # Include HTML representation of the DataFrame if required
            if task.include_html:
                task.html_result = result.to_html()

        except Exception as e:
            if task.optional:
                self.update_status(task, f'Failed (Optional): {str(e)}')
            else:
                self.update_status(task, f'Failed: {str(e)}')
            self.dual_logger.logger.error(f"QA task '{task.name}' failed with exception: {str(e)}")

    def execute_task_by_name(self, task_name):
        task = next((t for t in self.tasks if t.name == task_name), None)
        if task is None:
            raise TaskError(f"No task found with name '{task_name}'")
        self.execute_task(task)

    def execute_stage_by_number(self, stage_number):
        stage_tasks = [task for task in self.tasks if task.stage == stage_number]
        if not stage_tasks:
            error_message = f"No tasks found for stage {stage_number}"
            self.errors.append(error_message)
            self.dual_logger.logger.error(error_message)
        else:
            self.execute_stage(stage_tasks)

    def update_temp_table_list(self, task_name, table):
        self.temp_tables[task_name] = f'{table}'

    def update_status(self, task, status):
        update = {
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': status
        }

        if status == 'Completed':
            update['success'] = True
        elif status.startswith('Failed'):
            update['success'] = False

        if task.name not in self.status:
            self.status[task.name] = []
        self.status[task.name].append(update)

    def estimate_data_size(self, query):
        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        query_job = self.client.query(query, job_config=job_config)
        return query_job.total_bytes_processed

    def get_historical_data(self):
        query = f"""
        SELECT task_name, data_size, elapsed_time
        FROM `{self.translate_dataset('Silver')}.LKP_TASK_LOG`
        """
        df = self.client.query(query).to_dataframe()
        return df

    def estimate_run_time(self, estimated_data_size, task_name):
        df = self.get_historical_data()
        df_task = df[df['task_name'] == task_name]

        if df_task.empty:
            self.dual_logger.logger.info(f"No historical data available to estimate run time for task '{task_name}'")
            return None

        x = df_task['data_size'].values
        y = df_task['elapsed_time'].values
        estimated_time = np.interp(estimated_data_size, x, y)
        return estimated_time
    
    def send_completion_email(self):
        regular_status_summary = []
        qa_status_summary = []
        pass_flag = True

        for task_name, updates in self.status.items():
            latest_update = updates[-1]
            execution_time = self.task_execution_times.get(task_name, 'N/A')
            if isinstance(execution_time, (int, float)):
                execution_time_str = f"{execution_time:.2f} seconds"
            else:
                execution_time_str = execution_time
            task_summary = f"<span class='{ 'pass' if latest_update.get('success', False) else 'fail' }'>Task '{task_name}': {latest_update['status']}. (Execution Time: {execution_time_str})</span>"
            task = next((t for t in self.tasks if t.name == task_name), None)
            if task and task.is_qa:
                qa_status_summary.append(task_summary)
                # Include HTML result if available
                if hasattr(task, 'html_result'):
                    qa_status_summary.append(task.html_result)
            else:
                regular_status_summary.append(task_summary)
            if not latest_update.get('success', False) and not latest_update['status'].startswith('Failed (Optional)'):
                pass_flag = False

        summary = "<br>".join(regular_status_summary)
        qa_summary = "<br>".join(qa_status_summary)
        flag_text = "PASS" if pass_flag else "FAIL"
        total_execution_time = sum(time for time in self.task_execution_times.values() if isinstance(time, (int, float)))
        total_execution_time_str = f"{total_execution_time:.2f} seconds" if total_execution_time else "N/A"

        subject = f"{flag_text}: {self.name}"
        body = f"""
        <html>
            <head>
                <style>
                    .pass {{ color: #008000; }}
                    .fail {{ color: #FF0000; }}
                    .header {{ font-weight: bold; font-size: 16px; }}
                    .section {{ margin-bottom: 20px; }}
                    .summary {{ margin-left: 20px; }}
                </style>
            </head>
            <body>
                <div class="section">
                    <div class="header">Pipeline {self.name} Execution Status: {flag_text}</div>
                    <div class="summary">Total Execution Time: {total_execution_time_str}</div>
                </div>
                <div class="section">
                    <div class="header">Regular Tasks:</div>
                    <div class="summary">{summary}</div>
                </div>
                <div class="section">
                    <div class="header">QA Tasks:</div>
                    <div class="summary">{qa_summary}</div>
                </div>
            </body>
        </html>
        """

        try:
            self.send_email(subject, body)
            self.dual_logger.logger.info("Completion email sent successfully.")
        except Exception as e:
            self.dual_logger.logger.info(f"Failed to send completion email: {e}")
