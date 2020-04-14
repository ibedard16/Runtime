"""MEG UI Manager
"""

import pkg_resources
from PyQt5 import QtWidgets, QtGui, uic
import sys
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
            # Set handlers for main buttons
            # TODO: Add more handlers for these
            self._action_clone = self.findChild(QtWidgets.QAction, 'action_Clone')
            self._action_clone.triggered.connect(UIManager.open_clone_panel)
            self._action_open = self.findChild(QtWidgets.QAction, 'action_Open')
            self._action_open.triggered.connect(UIManager.open_clone_panel)
            self._action_quit = self.findChild(QtWidgets.QAction, 'action_Quit')
            self._action_quit.triggered.connect(sys.exit)
            self._action_about = self.findChild(QtWidgets.QAction, 'action_About')
            self._action_about.triggered.connect(UIManager.open_about)
            self._action_manage_plugins = self.findChild(QtWidgets.QAction, 'action_Manage_Plugins')
            self._action_manage_plugins.triggered.connect(UIManager.open_manage_plugins)
            # Set the open repository
            self._open_repo = None
            self.change_view(App.get_panel('MainPanel'))
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
    def open_about():
        """Open the about menu."""
        instance = UIManager.get_instance()
        desc = ('<center>'
                '<h1>Multimedia Extensible Git</h1>'
                '<p>Version 0.1</p>'
                '</center>')
        QtWidgets.QMessageBox.about(instance, "About MEG", desc)

    @staticmethod
    def open_manage_plugins():
        """Open the manage plugins window."""
        UIManager.change_view(App.refresh_panel('PluginsPanel'))

    @staticmethod
    def clone(username, password, repo_url, repo_path):
        """Clone a repository."""
        # TODO: Handle username + password
        # Set the config
        repo = GitManager.clone(repo_url, repo_path)
        if repo is not None:
            repos = Config.get('path/repos', defaultValue=[])
            repos.append({'url': repo_url, 'path': repo_path})
            Config.set('path/repos', repos)
            Config.save()
            UIManager.change_view(App.refresh_panel('RepoPanel', repo_url=repo_url, repo_path=repo_path, repo=repo))
        else:
            Logger.warning(f'MEG UIManager: Could not clone repo "{repo_url}"')
            alert = QtWidgets.QMessageBox()
            alert.setText(f'Could not clone the repo "{repo_url}"')
            alert.exec_()

    @staticmethod
    def open_repo(repo_url, repo_path):
        """Open a specific repo."""
        try:
            repo = GitRepository(repo_path)
            UIManager.change_view(App.refresh_panel('RepoPanel', repo_url=repo_url, repo_path=repo_path, repo=repo))
        except Exception as e:
            Logger.warning(f'MEG UIManager: {e}')
            Logger.warning(f'MEG UIManager: Could not load repo in "{repo_path}"')
            # Popup
            alert = QtWidgets.QMessageBox()
            alert.setText(f'Could not load the repo "{repo_path}"')
            alert.exec_()

    @staticmethod
    def setup(**kwargs):
        """Run initial setup of the UI manager."""
        instance = UIManager.get_instance(**kwargs)
        instance.show()

    @staticmethod
    def open_clone_panel():
        """"Download" or clone a project."""
        # TODO
        UIManager.change_view(App.refresh_panel('ClonePanel'))

    @staticmethod
    def return_to_main():
        """Return to the main panel"""
        UIManager.change_view(App.refresh_panel('MainPanel'))

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
