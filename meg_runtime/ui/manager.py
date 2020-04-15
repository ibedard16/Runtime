"""MEG UI Manager
"""

import pkg_resources
from PyQt5 import QtWidgets, QtGui, uic
from meg_runtime.config import Config
from meg_runtime.logger import Logger
from meg_runtime.app import App


class UIManager(QtWidgets.QMainWindow):
    """Main UI manager for the MEG system."""

    DEFAULT_UI_FILE = 'mainwindow.ui'

    # The singleton instance
    __instance = None

    def __init__(self, **kwargs):
        """UI manager constructor."""
        if UIManager.__instance is not None:
            # Except if another instance is created
            raise Exception(self.__class__.__name__ + " is a singleton!")
        else:
            super().__init__(**kwargs)
            UIManager.__instance = self
            # Load base panel resource
            path = pkg_resources.resource_filename(__name__, UIManager.DEFAULT_UI_FILE)
            try:
                uic.loadUi(path, self)
            except Exception as e:
                Logger.warning(f'MEG: BasePanel: {e}')
                Logger.warning(f'MEG: BasePanel: Could not load path {path}')
            # Set handlers for main buttons
            # TODO: Add more handlers for these
            self._action_clone = self.findChild(QtWidgets.QAction, 'action_Clone')
            self._action_clone.triggered.connect(App.open_clone_panel)
            self._action_open = self.findChild(QtWidgets.QAction, 'action_Open')
            self._action_open.triggered.connect(App.open_clone_panel)
            self._action_quit = self.findChild(QtWidgets.QAction, 'action_Quit')
            self._action_quit.triggered.connect(App.quit)
            self._action_about = self.findChild(QtWidgets.QAction, 'action_About')
            self._action_about.triggered.connect(App.open_about)
            self._action_manage_plugins = self.findChild(QtWidgets.QAction, 'action_Manage_Plugins')
            self._action_manage_plugins.triggered.connect(App.open_manage_plugins)
            # Set the default title
            self._update_title()
            # Set the icon
            icon_path = App.get_icon()
            if icon_path is not None:
                self.setWindowIcon(QtGui.QIcon(icon_path))

    @staticmethod
    def push_view(panel, closable=True):
        """Push a panel onto the stack being viewed."""
        if UIManager.__instance is not None:
            # Hide the current panel
            # if UIManager.__instance._current_panel:
            #     UIManager.__instance._current_panel.on_hide()
            # Show the current panel
            # panel.on_show()
            # Update the title for the panel
            UIManager.__instance._update_title(panel)
            # Get the window central widget
            container = UIManager.__instance.findChild(QtWidgets.QTabWidget, 'panelwidget')
            if container is not None:
                # Add the panel to the view stack
                widgets = panel.get_widgets()
                widgets.setParent(container)
                title = panel.get_title()
                index = container.addTab(widgets, 'Home' if not title else title)
                # Remove the close button if not closable
                if not closable:
                    tabbar = container.tabBar()
                    tabbar.tabButton(0, QtWidgets.QTabBar.RightSide).deleteLater()
                    tabbar.setTabButton(0, QtWidgets.QTabBar.RightSide, None)
                # Set the panel to the view
                container.setCurrentIndex(index)

    @staticmethod
    def pop_view():
        """Push a panel onto the stack being viewed."""
        if UIManager.__instance is not None:
            # Hide the current panel
            # if UIManager.__instance._current_panel:
            #     UIManager.__instance._current_panel.on_hide()
            # Show the current panel
            # panel.on_show()
            # Get the window central widget
            container = UIManager.__instance.findChild(QtWidgets.QWidget, 'centralwidget')
            if container:
                # Remove the panel from the view stack
                container.removeWidget(container.getCurrentIndex())
            # UIManager.__instance._update_title(panel)

    def _update_title(self, panel=None):
        """Update the window title from the current panel"""
        # Set the new window title, if provided by the panel
        if panel is not None and panel.get_title():
            self.setWindowTitle(f'{App.get_name()} - {panel.get_title()}')
        else:
            self.setWindowTitle(f'{App.get_name()}')
