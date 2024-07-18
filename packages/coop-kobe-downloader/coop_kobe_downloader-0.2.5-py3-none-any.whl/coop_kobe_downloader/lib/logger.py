import logging


def init_logger():
    """
    Set the log level.

    Returns:
      logging.Logger: The logger object.
    """
    # Create a logger object.
    logger = logging.getLogger(__name__)

    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    # Return the logger object.
    return logger
