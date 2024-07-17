import logging
from io import StringIO
from email.mime.text import MIMEText

class DualLogger:
    def __init__(self):
        self.log_stream = StringIO()
        self.console_handler = logging.StreamHandler()
        self.memory_handler = logging.StreamHandler(self.log_stream)

        logging.basicConfig(level=logging.DEBUG, handlers=[self.console_handler, self.memory_handler])
        self.logger = logging.getLogger('dual_logger')

    def log_and_print(self, message, level='info'):
        if level == 'info':
            self.logger.info(message)
        elif level == 'error':
            self.logger.error(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'debug':
            self.logger.debug(message)
        else:
            self.logger.info(message)
        print(message)  # Print to console

    def get_log_contents(self):
        return self.log_stream.getvalue()

    def attach_to_email(self, email_message):
        log_contents = self.get_log_contents()
        attachment = MIMEText(log_contents, 'plain')
        attachment.add_header('Content-Disposition', 'attachment', filename='pipeline_log.txt')
        email_message.attach(attachment)
