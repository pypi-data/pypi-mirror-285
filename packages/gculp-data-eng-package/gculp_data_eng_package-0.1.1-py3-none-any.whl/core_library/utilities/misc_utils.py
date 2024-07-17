"""
Utilites for miscellaneous reasons
"""
import logging
from hashlib import sha256
from typing import Any


def setup_console_logger(
    logger_name: str = "mds_logger", level: int = logging.DEBUG
) -> logging.Logger:
    """
    Create a python logger

    :param logger_name: logger name to set, defaults to __name__
    :type logger_name: _type_, optional
    :param level: log level, defaults to logging.DEBUG
    :type level: _type_, optional
    :return: the logger
    :rtype: logging.Logger
    """
    logger = logging.getLogger(logger_name)
    if not logger.handlers:
        # Create a logger
        logger = logging.getLogger(logger_name)

        # Set the logging level
        logger.setLevel(level)

        # Create a console handler and set its level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # Create a formatter and attach it to the handler
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)

        # Add the console handler to the logger
        logger.addHandler(console_handler)

    return logger


def hash_func(value: Any) -> str:
    """
    Hash an input using sha256

    :param value: Input to hash
    :type value: Any
    :return: SHA256 hash
    :rtype: str
    """
    result = sha256(value.encode("utf-8")).hexdigest()
    return result
