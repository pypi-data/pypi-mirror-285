import logging
import sys

# Note: use stringio to capture logs in memory to test against


def create_logger(name):
    # get logger
    logger = logging.getLogger(name)

    # clear previous logger
    logger.handlers.clear()

    # create formatter - (determines output format of log records)
    formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s")

    # create handlers - (determine where the log records get shipped to)
    stream_handler = logging.StreamHandler(
        sys.stdout
    )  # sends logs for stream handler to standard output

    # set formatters
    stream_handler.setFormatter(formatter)

    # add handlers to the logger
    logger.handlers = [stream_handler]

    # set log-level
    logger.setLevel(logging.DEBUG)

    return logger


default_logger = create_logger("default_logger")
