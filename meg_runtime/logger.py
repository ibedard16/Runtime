import logging


class Logger(object):
    """Base MEG logging class."""

    @staticmethod
    def debug(message):
        logger = logging.getLogger(__name__)
        logger.debug(message)

    @staticmethod
    def warning(message):
        logger = logging.getLogger(__name__)
        logger.debug(message)
