"""MEG UI Base Panel"""

import pkg_resources
from PyQt5 import QtWidgets, uic
from meg_runtime.logger import Logger


class BasePanel(QtWidgets.QMainWindow):
    """Base widget panel."""

    __widgets = None

    def __init__(self, **kwargs):
        """UI manager constructor."""
        super().__init__(**kwargs)
        self._load_ui_file()
        self.on_load()

    def get_class_widgets(self):
        """Get the class widgets of this panel."""
        return self.__widgets

    def get_widgets(self):
        """Get the widgets of this panel."""
        return self.get_class_widgets()

    def get_name(self):
        """Get the name of this panel."""
        return self.__class__.__name__

    def get_title(self):
        """Get the title of this panel."""
        return ''

    def on_load(self):
        """Load dynamic elements within the panel."""
        pass

    # Load the UI file
    def _load_ui_file(self):
        """Load the UI file from package resources"""
        path = pkg_resources.resource_filename(__name__, f'/{self.__class__.__name__.lower()}.ui')
        if not self.__class__.__widgets:
            try:
                self.__class__.__widgets = uic.loadUi(path)
            except Exception as e:
                Logger.warning(f'MEG: BasePanel: {e}')
                Logger.warning(f'MEG: BasePanel: Could not load path {path}')
