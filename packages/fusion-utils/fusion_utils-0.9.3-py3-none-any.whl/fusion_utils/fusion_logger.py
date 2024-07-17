import logging
from io import StringIO
from email.mime.text import MIMEText

class FusionLogger:
    def __init__(self):
        self.log_stream = StringIO()
        self.console_handler = logging.StreamHandler()
        self.memory_handler = logging.StreamHandler(self.log_stream)

        # Create a file handler
        self.file_handler = logging.FileHandler('pipeline_log.txt')

        logging.basicConfig(level=logging.INFO, handlers=[self.console_handler, self.memory_handler, self.file_handler])
        self.logger = logging.getLogger('FusionLogger')
        logging.getLogger().setLevel(logging.WARNING)
        self.logger.setLevel(logging.INFO)

    def log(self, message, level='info'):
        if level == 'info':
            self.logger.info(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'error':
            self.logger.error(message)
        elif level == 'critical':
            self.logger.critical(message)

    def get_log_contents(self):
        return self.log_stream.getvalue()

    def attach_to_email(self, email_message):
        log_contents = self.get_log_contents()
        attachment = MIMEText(log_contents, 'plain')
        attachment.add_header('Content-Disposition', 'attachment', filename='pipeline_log.txt')
        email_message.attach(attachment)
