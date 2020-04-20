"""MEG Application Class
"""

import sys
import pkg_resources
from PyQt5 import QtCore, QtWidgets
from meg_runtime.config import Config
from meg_runtime.logger import Logger
from meg_runtime.git import GitManager
from meg_runtime.plugins import PluginManager
from meg_runtime import ui


# MEG client application
class App(QtWidgets.QApplication):
    """Multimedia Extensible Git (MEG) Client Application"""

    NAME = 'Multimedia Extensible Git'
    VERSION = '0.1'
    ICON_PATH = 'ui/images/git.svg'
    URL = 'https://github.com/MultimediaExtensibleGit'

    __instance = None

    # Constructor
    def __init__(self):
        """Application constructor"""
        if App.__instance is not None:
            # Except if another instance is created
            raise Exception(self.__class__.__name__ + " is a singleton!")
        else:
            # Initialize super class constructor
            super().__init__([])
            App.__instance = self
            self._ui_manager = None
            self._main_panel = None
            self._prefs_panel = None
            self._plugins_panel = None
            self._clone_panel = None

    @staticmethod
    def get_instance():
        """Get the application instance"""
        return App.__instance

    @staticmethod
    def get_window():
        """Get the application window"""
        if App.__instance is None:
            return None
        return App.__instance._ui_manager

    @staticmethod
    def get_main_panel():
        """Get the main application panel"""
        if App.__instance is None:
            return None
        return App.__instance.main_panel()

    @staticmethod
    def get_prefs_panel():
        """Get the preferences application panel"""
        if App.__instance is None:
            return None
        return App.__instance.prefs_panel()

    @staticmethod
    def get_clone_panel():
        """Get the clone repository application panel"""
        if App.__instance is None:
            return None
        return App.__instance.clone_panel()

    @staticmethod
    def get_plugins_panel():
        """Get the manage plugins application panel"""
        if not App.__instance:
            return None
        return App.__instance.plugins_panel()

    @staticmethod
    def get_name():
        """Get application name"""
        return None if App.__instance is None else App.__instance.name()

    @staticmethod
    def get_version():
        """Get application version"""
        return None if App.__instance is None else App.__instance.version()

    @staticmethod
    def get_icon():
        """Get application icon path"""
        return None if App.__instance is None else App.__instance.icon()

    @staticmethod
    def get_url():
        """Get application URL"""
        return None if App.__instance is None else App.__instance.url()

    @staticmethod
    def quit(exit_code=0):
        if App.__instance is not None:
            App.__instance.exit(exit_code)

    def name(self):
        """Get application name"""
        return App.NAME

    def version(self):
        """Get application version"""
        return App.VERSION

    def icon(self):
        """Get the application icon path"""
        return pkg_resources.resource_filename(__name__, App.ICON_PATH)

    def url(self):
        """Get application URL"""
        return App.URL

    def main_panel(self):
        """Get the application main panel"""
        if self._main_panel is None:
            self._main_panel = ui.MainPanel()
        return self._main_panel

    def prefs_panel(self):
        """Get the application preferences panel"""
        if self._prefs_panel is None:
            self._prefs_panel = ui.PreferencesPanel()
        return self._prefs_panel

    def clone_panel(self):
        """Get the application clone repository panel"""
        if self._clone_panel is None:
            self._clone_panel = ui.ClonePanel()
        return self._clone_panel

    def plugins_panel(self):
        """Get the application manage plugins panel"""
        if self._plugins_panel is None:
            self._plugins_panel = ui.PluginsPanel()
        return self._plugins_panel

    def on_start(self):
        """On application start"""
        # Log information about version
        Logger.info(f'MEG: {App.NAME} Version {App.VERSION}')
        # Log debug information about home directory
        Logger.debug(f'MEG: Home <{Config.get("path/home")}>')
        # Load configuration
        Config.load()
        # Log debug information about cache and plugin directories
        Logger.debug(f'MEG: Cache <{Config.get("path/cache")}>')
        Logger.debug(f'MEG: Plugins <{Config.get("path/plugins")}>')
        # Update plugins information
        PluginManager.update()
        # Load enabled plugins
        PluginManager.load_enabled()

    # On application stopped
    def on_stop(self):
        """On application stopped"""
        # Unload the plugins
        PluginManager.unload_all()
        # Write the exit message
        Logger.debug(f'MEG: Quit')

    # Run the application
    @staticmethod
    def run(**kwargs):
        """Run the application UI"""
        if App.__instance is None:
            App()
        if App.__instance is not None:
            # On application start
            instance = App.get_instance()
            instance.on_start()
            # Run the UI
            ui_manager = ui.UIManager(**kwargs)
            instance._ui_manager = ui_manager
            # Show the main panel
            App.return_to_main()
            # Show the window
            ui_manager.show()
            # Launch application
            ret = instance.exec_()
            # On application stop
            instance.on_stop()
            # Exit the application
            instance.exit(ret)

    @staticmethod
    def open_credential_dialog():
        """Open a credential dialog for the user and return (username, password)."""
        # Setup the dialog
        dialog = QtWidgets.QDialog()
        spacer = QtWidgets.QVBoxLayout()
        spacer.addWidget(QtWidgets.QLabel('Username'))
        username = QtWidgets.QLineEdit()
        spacer.addWidget(username)
        spacer.addWidget(QtWidgets.QLabel('Password'))
        password = QtWidgets.QLineEdit()
        password.setEchoMode(QtWidgets.QLineEdit.Password)
        spacer.addWidget(password)
        # Add the close button
        button = QtWidgets.QPushButton('OK')
        button.clicked.connect(dialog.accept)
        spacer.addWidget(button)
        dialog.setLayout(spacer)
        # Execute it
        dialog.exec_()
        return (username.text(), password.text())

    @staticmethod
    def open_about():
        """Open the about menu."""
        desc = (f'<center><h2>{App.get_name()}</h2>'
                f'<p><b>Version {App.get_version()}</b><br/>'
                f'<a href="{App.get_url()}">{App.get_url()}</a></p>'
                f'<p>Qt version {QtCore.QT_VERSION_STR}<br/>'
                f'PyQt version {QtCore.PYQT_VERSION_STR}<br/>'
                f'Python version {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}<br/>'
                f'Font Awesome version 5.13.0</p></center>')
        QtWidgets.QMessageBox.about(App.get_window(), f'About {App.get_name()}', desc)

    @staticmethod
    def open_prefs_panel():
        """Open the preferences."""
        App.get_window().set_view(App.get_prefs_panel())

    @staticmethod
    def open_plugins_panel():
        """Open the manage plugins."""
        App.get_window().set_view(App.get_plugins_panel())

    @staticmethod
    def open_clone_panel():
        """Clone a repository."""
        App.get_window().set_view(App.get_clone_panel())

    @staticmethod
    def open_manage_roles(repo):
        """Open the manage plugins window."""
        App.get_window().push_view(ui.RolesPanel(repo))

    @staticmethod
    def open_repo_panel():
        """Open a repository."""
        dialog = QtWidgets.QFileDialog()
        # Only allow directories
        dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
        if dialog.exec_():
            repo = GitManager.open(dialog.selectedFiles()[0])
            App.get_window().push_view(ui.RepoPanel(repo))
            App.save_repo_entry(repo.path)

    @staticmethod
    def return_to_main():
        """Return to the main panel"""
        App.get_window().set_view(App.get_main_panel())

    @staticmethod
    def save_repo_entry(repo_path, repo_url=None):
        repos = Config.get('repos', defaultValue=[])
        duplicate_found = False
        for index, repo in enumerate(repos):
            if repo['path'] == repo_path:
                repos[index]['url'] = repo_url
                duplicate_found = True
                break
        if not duplicate_found:
            repos.append({'path': repo_path, 'url': repo_url})
        Config.set('repos', repos)
        Config.save()
