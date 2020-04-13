"""MEG UI Manager
"""

import pkg_resources
from PyQt5 import QtWidgets, QtGui, uic
from meg_runtime.config import Config
from meg_runtime.logger import Logger
from meg_runtime.git import GitManager, GitRepository
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
            # Set the open repository
            self._open_repo = None
            #self.change_view(App.get_panel('MainPanel'))
            self.change_view(App.get_panel('PluginsPanel'))
            # Set the icon
            icon_path = App.get_icon()
            if icon_path is not None:
                self.setWindowIcon(QtGui.QIcon(icon_path))

    @staticmethod
    def get_instance(**kwargs):
        """Get an instance of the singleton."""
        if UIManager.__instance is None:
            UIManager(**kwargs)
        return UIManager.__instance

    @staticmethod
    def setup(**kwargs):
        """Run initial setup of the UI manager."""
        instance = UIManager.get_instance(**kwargs)
        instance.show()

    @staticmethod
    def open_clone_panel():
        """"Download" or clone a project."""
        # TODO
        UIManager.change_view(App.get_panel('ClonePanel'))

    @staticmethod
    def open_plugins_panel():
        """Manage installed plugins"""
        UIManager.change_view(App.get_panel('PluginsPanel'))

    @staticmethod
    def return_to_main():
        """Return to the main panel"""
        UIManager.change_view(App.get_panel('MainPanel'))

    @staticmethod
    def get_changes(repo):
        """Get changes for the given repo (do a pull)."""
        repo.pull()

    @staticmethod
    def send_changes(repo):
        """Send changes for the given repo."""
        # TODO
        pass

    @staticmethod
    def change_view(panel):
        """Change the current panel being viewed. """
        # Reload the panel before changing the view
        instance = UIManager.get_instance()
        if panel and panel.get_title():
            instance.setWindowTitle(f'{App.get_name()} - {panel.get_title()}')
        else:
            instance.setWindowTitle(f'{App.get_name()}')
        container = instance.findChild(QtWidgets.QWidget, 'centralwidget')
        if container is not None:
            widget = None if not panel else panel.get_widgets()
            layout = container.layout()
            if layout is not None:
                for i in reversed(range(layout.count())): 
                    layout.itemAt(i).widget().setParent(None)
                if widget:
                    layout.addWidget(widget)
            if widget:
                widget.setParent(container)

    # TODO: Add more menu opening/closing methods here
