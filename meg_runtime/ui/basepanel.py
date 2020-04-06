"""MEG UI Base Panel
"""
from PyQt5 import QtWidgets, uic

import pkg_resources

from meg_runtime.logger import Logger


class BasePanel(QtWidgets.QMainWindow):
    """Base widget panel."""

    def __init__(self, **kwargs):
        """UI manager constructor."""
        super().__init__(**kwargs)
        # Load the UI file
        path = pkg_resources.resource_filename(
            __name__,
            f'/{self.__class__.__name__.lower()}.ui'
        )
        try:
            uic.loadUi(path, self)
        except Exception as e:
            Logger.warning('MEG: BasePanel: {}'.format(e))
            Logger.warning('MEG: BasePanel: Could not load path {}'.format(path))


