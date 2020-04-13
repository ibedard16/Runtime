"""MEG Application Class
"""

import sys
import pkg_resources
from PyQt5 import QtWidgets
from meg_runtime.config import Config
from meg_runtime.plugins import PluginManager
from meg_runtime.logger import Logger
from meg_runtime import ui


# MEG client application
class App(QtWidgets.QApplication):
    """Multimedia Extensible Git (MEG) Client Application"""

    APP_NAME = 'Multimedia Extensible Git'
    APP_ICON_PATH = 'meg.ico'
    PANELS = [
        'MainPanel',
        'ClonePanel',
        'RepoPanel',
        'PluginsPanel',
    ]

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
            self._panels = None

    @staticmethod
    def get_name():
        """Get application name"""
        return None if not App.__instance else App.__instance.name()

    @staticmethod
    def get_icon():
        return None if not App.__instance else App.__instance.icon()

    @staticmethod
    def get_all_panels():
        """Get all panels"""
        return None if not App.__instance else App.__instance.all_panels()

    @staticmethod
    def get_panels():
        """Get all name and panel pairs"""
        return None if not App.__instance else App.__instance.panels()

    @staticmethod
    def get_panel(name):
        """Get a panel by name"""
        return None if not App.__instance else App.__instance.panel(name)

    @staticmethod
    def refresh_panel(name, **kwargs):
        """Refresh a panel by name."""
        instance = App.__instance
        if instance is None:
            return None
        if name in App.PANELS:
            try:
                panel_ctor = getattr(ui, name)
                panel_obj = panel_ctor(**kwargs)
                instance._panels[panel_obj.get_name()] = panel_obj
                return panel_obj
            except Exception as e:
                Logger.warning(f'MEG UI: {e}')
                Logger.warning(f'MEG UI: Could not create panel "{name}"')
        else:
            Logger.warning(f'MEG UI: Panel does not exist')

        return None

    def name(self):
        """Get application name"""
        return App.APP_NAME

    def icon(self):
        return pkg_resources.resource_filename(__name__, App.APP_ICON_PATH)

    def all_panels(self):
        """Get all panels"""
        panels = self.panels()
        return [] if not panels else panels.values()

    def panels(self):
        """Get all name and panel pairs"""
        if not self._panels:
            self._panels = {}
            for panel in App.PANELS:
                try:
                    panel_ctor = getattr(ui, panel)
                    panel_obj = panel_ctor()
                    self._panels[panel_obj.get_name()] = panel_obj
                except Exception as e:
                    Logger.warning(f'MEG UI: {e}')
                    Logger.warning(f'MEG UI: Could not create panel "{panel}"')
        return self._panels

    def panel(self, name):
        """Get a panel by name"""
        panels = self.get_panels()
        return None if not panels or name not in panels else panels[name]

    def on_start(self):
        """On application start"""
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
            ui.UIManager.setup(**kwargs)
            # Launch application
            ret = App.__instance.exec_()
            # On application stop
            App.__instance.on_stop()
            # Exit
            sys.exit(ret)
