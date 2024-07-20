import sys
import logging


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Sets up a logger with the specified name and logging level.

    Args:
        name (str): Name of the logger.
        level (int): Logging level (default is logging.INFO).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a stream handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(level)

    # Create a formatter and set it for the handler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stream_handler.setFormatter(formatter)

    # Add the handler to the logger
    if not logger.handlers:
        logger.addHandler(stream_handler)

    return logger
