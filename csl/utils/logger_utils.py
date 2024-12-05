"""
Logger Utilities Module.

This module provides utilities for customizing logging behavior, such as
defining custom log levels, applying colors to log messages, and adding
console handlers to the logger.
"""

import logging

# Define custom log levels and their associated colors
custom_levels = {
    'DEBUG': '\033[94m',    # Light Blue
    'INFO': '\033[92m',     # Green
    'WARNING': '\033[93m',  # Yellow
    'ERROR': '\033[91m',    # Red
    'CRITICAL': '\033[91m'  # Red
}


# Define a custom formatter
class ColoredFormatter(logging.Formatter):
    """
    A custom log formatter that adds color to log messages based on their
    severity level.
    """
    def format(self, record):
        """
        Format the log message with color based on the log level.

        Args:
            record (logging.LogRecord): The log record containing the log
            message and associated metadata.

        Returns:
            str: The formatted log message with the appropriate color.
        """
        levelname = record.levelname
        msg = super().format(record)
        color_prefix = custom_levels.get(levelname, '\033[0m')  # Default to no color if level not found
        return f'{color_prefix}{msg}\033[0m'  # Append color reset code after the message


def setup_logger(log_fpath):
    """Add a console handler to the root logger with a colored log formatter."""

    # Get the logger
    logger = logging.getLogger()

    if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
        logging.basicConfig(filename='{}.log'.format(log_fpath), level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Create a console handler
        console_handler = logging.StreamHandler()
        # Set the custom formatter
        formatter = ColoredFormatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        # Add the console handler to the logger
        logger.addHandler(console_handler)
