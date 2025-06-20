from csl.utils import setup_logger, ColoredFormatter
from unittest.mock import patch
import logging


def test_setup_logger():
    """Tests that a new StreamHandler with a ColoredFormatter is added to the logger if none exists."""
    # Patch StreamHandler and getLogger
    with patch('logging.getLogger') as mock_get_logger, \
         patch('logging.StreamHandler') as mock_stream_handler:

        # Create a mock logger
        mock_logger_setup = mock_get_logger.return_value
        # Create a mock StreamHandler
        mock_handler_instance = mock_stream_handler.return_value

        # Call the function to add the console logger
        setup_logger('dummy/path')

        # Make sure the StreamHandler was instantiated
        mock_stream_handler.assert_called_once()

        # Ensure setFormatter was called on the handler instance with ColoredFormatter
        mock_handler_instance.setFormatter.assert_called_once()
        formatter_arg = mock_handler_instance.setFormatter.call_args[0][0]
        assert isinstance(formatter_arg, ColoredFormatter)

        # Ensure addHandler was called on the logger with the handler instance
        mock_logger_setup.addHandler.assert_called_once_with(mock_handler_instance)


def test_setup_logger_existing_handler():
    """Tests that no additional StreamHandler is added if one already exists in the logger's handlers."""
    # Patch StreamHandler and getLogger
    with patch('logging.getLogger') as mock_get_logger:
        # Create a mock logger
        mock_logger_setup = mock_get_logger.return_value

        # Create a real StreamHandler and add it to the mock logger's handlers list
        existing_handler = logging.StreamHandler()
        mock_logger_setup.handlers = [existing_handler]

        # Call the function to add the console logger
        setup_logger('dummy/path')

        # Ensure no new StreamHandler was added since one already exists
        assert len(mock_logger_setup.handlers) == 1
        assert mock_logger_setup.handlers[0] is existing_handler
