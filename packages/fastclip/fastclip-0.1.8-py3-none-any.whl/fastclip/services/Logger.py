import traceback
import logging


EMPTY_STACK_TRACE = "NoneType: None\n"


class Logger:
    """A generic logger class that can be used to log messages at different levels."""

    logger: logging.Logger

    def __init__(self, app_name: str, log_level: int = logging.INFO):
        self.logger = logging.getLogger(app_name)

        self.logger.setLevel(log_level)

        # Remove existing handlers to prevent duplicate logs
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # Add correct log formatting
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log(self, level: int, message: str):
        self.logger.log(level, message)

    def debug(self, message: str):
        self.log(logging.DEBUG, message)

    def info(self, message: str):
        self.log(logging.INFO, message)

    def warning(self, message: str):
        self.log(logging.WARNING, message)

    def error(self, message: str):
        stack_trace = traceback.format_exc()
        if stack_trace != EMPTY_STACK_TRACE:
            # Add traceback to the error message if there is one
            # When this is called outside a try/except block, the stack trace is empty
            message = f"{message}\nStack trace:\n{traceback.format_exc()}"

        self.log(logging.ERROR, message)
