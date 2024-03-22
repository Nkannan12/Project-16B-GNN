import os
import logging
from logging import handlers
class Logger(object):
    """Logger class for logging messages to a file and console.

    Methods:
        __init__(self): Initializes the Logger object.
        set_logger(self, log_path): Configures the logger to log messages to a file and console.
    """
    
    def __init__(self):
        """
        Initializes the object.
        """
        pass
    
    def set_logger(self, log_path):
        """Configures the logger to log messages to a file and console.

        Args:
            log_path (str): Path to the log file.

        Returns:
            None
        """
        if os.path.exists(log_path) is True:
           os.remove(log_path)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
    
        if not self.logger.handlers:
            # To a file
            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
            self.logger.addHandler(file_handler)
    
            # To console
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(stream_handler)
