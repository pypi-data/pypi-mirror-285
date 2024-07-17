import sys
from loguru import logger


def configure_logger(debug: bool):
    logger.remove()

    if debug:
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.add(sys.stderr, level="INFO")
