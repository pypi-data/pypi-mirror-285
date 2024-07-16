"""This module provides some functionalities for logging."""
import logging
import os
import sys
import time
from collections import deque, namedtuple

LogEntry = namedtuple("LogEntry", ["message", "start_time", "logger"])  # Container for log entries.
log_stack = deque()  # Stack where the log-entries are collected.


def log_start(message, logger):
    """Logs the start of a process step.

    Args:
        message (str): message to log.
        logger (Logger): instance of the logger where the message should be logged.
    """
    log_stack.append(LogEntry(message, time.time(), logger))
    logger.info("({}) start {}.".format(len(log_stack), message))


def log_end(additional_message=None):
    """Logs the end of a process step together with the start message and the time elapsed.

    Args:
        additional_message (str): Additional message, which is added to the message from the start log.
    """
    n = len(log_stack)
    log_entry = log_stack.pop()
    log_message = "({}) end {}. time elapsed: {}{}".format(n, log_entry.message,
                                                           seconds_to_hhmmssms(time.time() - log_entry.start_time),
                                                           ". {}. ".format(
                                                               additional_message) if additional_message else ".")
    log_entry.logger.info(log_message)


def init_logging(directory, file_name, log_level=logging.INFO):
    """Initializes the logger for the project.

    Args:
        directory (str): Path to the folder where the log file is written.
        file_name (str): Name of the log file.
        log_level (int): log level
    """
    logger = logging.getLogger()
    logger.level = log_level
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    file_handler = logging.FileHandler(os.path.join(directory, file_name), mode="w")
    file_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)


def seconds_to_hhmmssms(seconds):
    """Parses the number of seconds after midnight and returns the corresponding HH:MM:SS.f-string.

    Args:
        seconds (float): number of seconds after midnight.

    Returns:
        str: the corresponding HH:MM:SS.f-string.
    """
    int_seconds = int(seconds)
    ms = round((seconds - int_seconds) * 1000)
    m, s = divmod(int_seconds, 60)
    h, m = divmod(m, 60)
    return "{:02d}:{:02d}:{:02d}.{:03d}".format(int(h), int(m), int(s), int(ms))
