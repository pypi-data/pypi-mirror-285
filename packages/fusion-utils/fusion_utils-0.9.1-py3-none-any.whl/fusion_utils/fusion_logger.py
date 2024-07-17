import logging
from io import StringIO
from email.mime.text import MIMEText

class FusionLogger:
    def __init__(self, log_filename='pipeline.log'):
        self.log_stream = StringIO()
        self.log_filename = log_filename

        self.file_handler = logging.FileHandler(log_filename)
        self.memory_handler = logging.StreamHandler(self.log_stream)

        logging.basicConfig(level=logging.INFO, handlers=[self.file_handler, self.memory_handler])
        self.logger = logging.getLogger('fusion_logger')

    def get_log_contents(self):
        return self.log_stream.getvalue()

    def attach_to_email(self, email_message):
        with open(self.log_filename, 'r') as log_file:
            log_contents = log_file.read()
        attachment = MIMEText(log_contents, 'plain')
        attachment.add_header('Content-Disposition', 'attachment', filename='pipeline_log.txt')
        email_message.attach(attachment)

    def log(self, message, level='info'):
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
