"""MEG UI Base Panel"""

import pkg_resources
from PyQt5 import QtGui, QtWidgets, uic
from meg_runtime.logger import Logger
from meg_runtime.app import App


class BasePanel(QtWidgets.QMainWindow):
    """Base widget panel."""

    __widgets = None
    __icon = None

    def __init__(self, icon_path=None, **kwargs):
        """UI manager constructor."""
        super().__init__(**kwargs)
        self._widgets = None
        self._load_ui_file()
        self.reload(icon_path)

    def __del__(self):
        """UI manager destructor"""
        self.on_unload()

    def reload(self, icon_path=None):
        """Reload the widgets of this panel from the class widgets"""
        if self.__class__.__widgets is not None:
            # Unload previous dynamic widgets, if any
            if self._widgets:
                self.on_unload()
            # Create the new root widget
            self._widgets = self.__class__.__widgets[1]()
            # Setup the root widget UI
            self.__class__.__widgets[0]().setupUi(self._widgets)
        # Set the panel icon
        self._icon = self.__class__.__icon if icon_path is None else QtGui.QIcon(icon_path)
        # Load the dynamic widgets
        self.on_load()

    def get_widgets(self):
        """Get the widgets of this panel."""
        return self._widgets

    def get_name(self):
        """Get the name of this panel."""
        return self.__class__.__name__

    def get_title(self):
        """Get the title of this panel."""
        return ''

    def get_icon(self):
        """Get the icon image of this panel."""
        return self._icon

    def get_is_closable(self):
        """Get if the panel is closable."""
        return True

    def on_load(self):
        """Load dynamic elements within the panel."""
        pass

    def on_unload(self):
        """Unload dynamic elements within the panel."""
        pass

    def on_show(self):
        """Showing the panel."""
        pass

    def on_hide(self):
        """Hiding the panel."""
        pass

    def on_close(self):
        """Closing the panel."""
        pass

    def visible(self):
        """Panel is visible."""
        return self in App.get_window().get_panels()

    # Load the UI file
    def _load_ui_file(self):
        """Load the UI file from package resources"""
        if not self.__class__.__widgets:
            path = pkg_resources.resource_filename(__name__, f'/{self.__class__.__name__.lower()}.ui')
            try:
                self.__class__.__widgets = uic.loadUiType(path)
            except Exception as e:
                Logger.warning(f'MEG UI: {e}')
                Logger.warning(f'MEG UI: Could not load UI path <{path}>')
        # Set the icon for the instance
        if not self.__class__.__icon:
            icon_path = pkg_resources.resource_filename(__name__, f'/images/{self.__class__.__name__.lower()}.svg')
            try:
                self.__class__.__icon = QtGui.QIcon(icon_path)
            except Exception as e:
                Logger.warning(f'MEG UI: {e}')
                Logger.warning(f'MEG UI: Could not load icon path <{path}>')
