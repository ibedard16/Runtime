"""MEG Application Class
"""

import pkg_resources
from PyQt5 import QtWidgets
from meg_runtime.config import Config
from meg_runtime.logger import Logger
from meg_runtime.git import GitManager, GitRepository
from meg_runtime.plugins import PluginManager
from meg_runtime import ui


# MEG client application
class App(QtWidgets.QApplication):
    """Multimedia Extensible Git (MEG) Client Application"""

    NAME = 'Multimedia Extensible Git'
    VERSION = '0.1'
    ICON_PATH = 'meg.ico'

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

    @staticmethod
    def get_instance():
        """Get the application instance"""
        return App.__instance

    @staticmethod
    def get_window():
        """Get the application window"""
        if not App.__instance:
            return None
        return App.__instance._ui_manager

    @staticmethod
    def get_name():
        """Get application name"""
        return None if not App.__instance else App.__instance.name()

    @staticmethod
    def get_version():
        """Get application version"""
        return None if not App.__instance else App.__instance.version()

    @staticmethod
    def get_icon():
        return None if not App.__instance else App.__instance.icon()

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
        return pkg_resources.resource_filename(__name__, App.ICON_PATH)

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
        if not App.__instance:
            App()
        if App.__instance:
            # On application start
            App.__instance.on_start()
            # Run the UI
            ui_manager = ui.UIManager(**kwargs)
            App.__instance._ui_manager = ui_manager
            # Set the main panel to start
            ui_manager.push_view(ui.MainPanel(), False)
            # Show the window
            ui_manager.show()
            # Launch application
            ret = App.__instance.exec_()
            # On application stop
            App.__instance.on_stop()
            # Exit the application
            App.__instance.exit(ret)

    @staticmethod
    def open_about():
        """Open the about menu."""
        desc = (f'<center><h3>{App.get_name()}</h3><p>Version {App.get_version()}</p></center>')
        QtWidgets.QMessageBox.about(App.get_window(), f'About {App.get_name()}', desc)

    @staticmethod
    def open_manage_plugins():
        """Open the manage plugins window."""
        ui.UIManager.push_view(ui.PluginsPanel())

    @staticmethod
    def open_add_plugin():
        """"Open the new plugin window"""
        ui.UIManager.push_view(ui.AddPluginPanel())

    @staticmethod
    def open_manage_roles():
        """Open the manage plugins window."""
        ui.UIManager.push_view(ui.RolesPanel())


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
            ui.UIManager.push_view(ui.RepoPanel(repo_url=repo_url, repo_path=repo_path, repo=repo))
        else:
            Logger.warning(f'MEG UIManager: Could not clone repo "{repo_url}"')
            alert = QtWidgets.QMessageBox()
            alert.setText(f'Could not clone the repo "{repo_url}"')
            alert.exec_()

    @staticmethod
    def open_repo(repo_url, repo_path):
        """Open a specific repo."""
        # try:
        repo = GitRepository(repo_path)
        ui.UIManager.push_view(ui.RepoPanel(repo_url=repo_url, repo_path=repo_path, repo=repo))
        # except Exception as e:
        #     Logger.warning(f'MEG UIManager: {e}')
        #     Logger.warning(f'MEG UIManager: Could not load repo in "{repo_path}"')
        #     # Popup
        #     alert = QtWidgets.QMessageBox()
        #     alert.setText(f'Could not load the repo "{repo_path}"')
        #     alert.exec_()

    @staticmethod
    def open_clone_panel():
        """"Download" or clone a project."""
        # TODO
        ui.UIManager.push_view(ui.ClonePanel())

    @staticmethod
    def return_to_main():
        """Return to the main panel"""
        ui.UIManager.push_view(ui.MainPanel())

    @staticmethod
    def get_changes(repo):
        """Get changes for the given repo (do a pull)."""
        repo.pull()

    @staticmethod
    def send_changes(repo):
        """Send changes for the given repo."""
        # TODO
        pass

    # TODO: Add more menu opening/closing methods here
