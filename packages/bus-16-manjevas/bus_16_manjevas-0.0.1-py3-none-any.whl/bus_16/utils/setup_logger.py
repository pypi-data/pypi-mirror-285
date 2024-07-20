import logging


def create_logger(name, log_file, level=logging.INFO):
    """create a logger instance

    Args:
        name (str): Name of logger, can be hierarchial
        log_file (str): Log file path
        level (logging.level, optional): Logging level at which log is store to file. Defaults to logging.INFO.

    Returns:
        logging.getLogger: Logger object
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a file handler for this logger
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter(
        "%(asctime)s, %(name)s, %(funcName)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
