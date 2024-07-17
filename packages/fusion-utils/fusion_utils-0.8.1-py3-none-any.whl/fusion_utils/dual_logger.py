import logging
import sys

class DualLogger(logging.Handler):
    def __init__(self, log_stream):
        super().__init__()
        self.log_stream = log_stream
        self.console_handler = logging.StreamHandler(sys.stdout)

    def emit(self, record):
        msg = self.format(record)
        self.log_stream.write(msg + '\n')
        self.console_handler.emit(record)