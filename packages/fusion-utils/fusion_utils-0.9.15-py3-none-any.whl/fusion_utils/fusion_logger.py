import logging
from io import StringIO
from email.mime.text import MIMEText

class FusionLogger:
    def __init__(self):
        self.log_stream = StringIO()

        # Set up the console handler
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.INFO)

        # Set up the memory handler
        self.memory_handler = logging.StreamHandler(self.log_stream)
        self.memory_handler.setLevel(logging.INFO)

        # Set up the file handler
        self.file_handler = logging.FileHandler('pipeline_log.txt')
        self.file_handler.setLevel(logging.INFO)
        root_logger = logging.getLogger()
        # Clear any existing handlers
        if root_logger.hasHandlers():
            root_logger.handlers.clear()

        # Create the logger
        self.logger = logging.getLogger('FusionLogger')
        self.logger.setLevel(logging.INFO)

        # Create a custom formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Set the formatter for all handlers
        self.console_handler.setFormatter(formatter)
        self.memory_handler.setFormatter(formatter)
        self.file_handler.setFormatter(formatter)

        # Add handlers to the logger
        self.logger.addHandler(self.console_handler)
        self.logger.addHandler(self.memory_handler)
        self.logger.addHandler(self.file_handler)

        # Prevent propagation to the root logger
        self.logger.propagate = False

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

# Example usage
logger = FusionLogger()
logger.log("This is an info message")
logger.log("This is a warning message", level='warning')
logger.log("This is an error message", level='error')

print('LOG IS BELOW ==========================')
print(logger.get_log_contents())
