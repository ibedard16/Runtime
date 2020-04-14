import sys
import logging


class Logger(object):
    """Base MEG logging class."""

    __instance = None

    def __init__(self, **kwargs):
        if Logger.__instance is not None:
            # Except if another instance is created
            raise Exception(self.__class__.__name__ + " is a singleton!")
        else:
            super().__init__(**kwargs)
            Logger.__instance = self
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.DEBUG)
            self.logger.addHandler(handler)

    @staticmethod
    def debug(message):
        if Logger.__instance is None:
            Logger()
        if Logger.__instance and Logger.__instance.logger:
            Logger.__instance.logger.debug(message)

    @staticmethod
    def info(message):
        if Logger.__instance is None:
            Logger()
        if Logger.__instance and Logger.__instance.logger:
            Logger.__instance.logger.info(message)

    @staticmethod
    def warning(message):
        if Logger.__instance is None:
            Logger()
        if Logger.__instance and Logger.__instance.logger:
            Logger.__instance.logger.warning(message)
