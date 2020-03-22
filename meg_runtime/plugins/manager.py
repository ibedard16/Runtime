"""Multimedia Extensible Git (MEG) plugin manager

Plugin manager for runtime
"""

import os
import sys
import shutil
from kivy.logger import Logger
from meg_runtime.config import Config
from meg_runtime.plugins import Plugin, PluginInformation, PluginException
from meg_runtime.git import GitRepository, GitException, GitManager


# Runtime plugin manager
class PluginManager(dict):
    """Runtime plugin manager"""

    # The default plugin cache repository URL
    DEFAULT_CACHE_URL = 'https://github.com/MultimediaExtensibleGit/Plugins.git'
    # The defautl bare repository path
    DEFAULT_BARE_REPO_PATH = '.git'

    # The plugin manager instance
    __instance = None

    # Plugin manager constructor
    def __init__(self, update=True, **kwargs):
        """Plugin manager constructor"""
        # Check if there is already a plugin manager instance
        if PluginManager.__instance is not None:
            # Except if another instance is created
            raise PluginException(self.__class__.__name__ + " is a singleton!")
        else:
            # Initialize super class constructor
            super().__init__(**kwargs)
            # Set this as the current plugin manager instance
            PluginManager.__instance = self
            # Set plugin and cache paths in python path for import, the first path may
            #  be the Kivy library zip so check and insert one path later if that is the case
            i = (3, 2)[os.path.isdir(sys.path[0])]
            sys.path.insert(i, Config.get('path/cache'))
            sys.path.insert(i, Config.get('path/plugins'))
            # Load information about plugins
            if update:
                PluginManager.update()

    # Clean caches and plugins
    @staticmethod
    def clean():
        """Clean caches and plugins"""
        retval = PluginManager.clean_cache()
        retval = PluginManager.clean_plugins() and retval
        return PluginManager.clean_plugin_cache() and retval

    # Clean dependency cache
    @staticmethod
    def clean_cache():
        """Clean dependency cache"""
        # Remove the cache directory or the block file
        cache_path = Config.get('path/cache')
        if isinstance(cache_path, str) and os.path.exists(cache_path):
            try:
                if os.path.isdir(cache_path):
                    # Remove cache directory
                    shutil.rmtree(cache_path)
                else:
                    # Remove cache directory block file
                    os.remove(cache_path)
            except Exception:
                return False
        return True

    # Clean plugins
    @staticmethod
    def clean_plugins():
        """Clean plugins"""
        # Remove the plugins directory or the block file
        plugins_path = Config.get('path/plugins')
        if isinstance(plugins_path, str) and os.path.exists(plugins_path):
            try:
                if os.path.isdir(plugins_path):
                    # Remove plugins directory
                    shutil.rmtree(plugins_path)
                else:
                    # Remove plugins directory block file
                    os.remove(plugins_path)
            except Exception:
                return False
        return True

    # Clean plugin cache
    @staticmethod
    def clean_plugin_cache():
        """Clean plugin cache"""
        # Remove the plugin cache directory or the block file
        plugin_cache_path = Config.get('path/plugin_cache')
        if isinstance(plugin_cache_path, str) and os.path.exists(plugin_cache_path):
            try:
                if os.path.isdir(plugin_cache_path):
                    # Remove plugin cache directory
                    shutil.rmtree(plugin_cache_path)
                else:
                    # Remove plugin cache directory block file
                    os.remove(plugin_cache_path)
            except Exception:
                return False
        return True

    # Update local plugin information
    @staticmethod
    def update():
        """Update local plugin information"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager(False)
        if PluginManager.__instance is None:
            return False
        # Log updating plugin information
        Logger.debug(f'MEG Plugins: Updating plugin information')
        # Unload all plugins
        PluginManager.unload_all()
        # Clear previous plugin information
        if 'plugins' not in PluginManager.__instance or not isinstance(PluginManager.__instance['plugins'], dict):
            PluginManager.__instance['plugins'] = {}
        # Obtain the available plugins from the plugins path
        retval = True
        for (path, dirs, files) in os.walk(Config.get('path/plugins')):
            # For each plugin load the information
            for d in dirs:
                # Log debug information about the plugin
                plugin_path = path + os.sep + d
                Logger.debug(f'MEG Plugins: Found plugin information <{plugin_path}>')
                try:
                    # Get the plugin path and load plugin information
                    plugin = PluginManager._update(plugin_path)
                    if plugin is not None:
                        # Log plugin information
                        PluginManager._log_plugin(plugin)
                        # Add the plugin
                        PluginManager.__instance['plugins'][plugin.name()] = plugin
                except Exception as e:
                    # Log that loading the plugin information failed
                    Logger.warning(f'MEG Plugins: {e}')
                    Logger.warning(f'MEG Plugins: Could not load information for plugin <{plugin_path}>')
                    retval = False
            # Do not actually walk the directory tree, only get directories directly under plugins path
            break
        return retval

    # Update cached plugin information
    @staticmethod
    def update_cache():
        """Update cached plugin information"""
        # Check there is plugin manager instance
        update = False
        if PluginManager.__instance is None:
            PluginManager(False)
            update = True
        if PluginManager.__instance is None:
            return False
        # Log updating plugin information
        Logger.debug(f'MEG Plugins: Updating plugin cache')
        # Clear previous plugin cache information
        if 'plugin_cache' not in PluginManager.__instance or not isinstance(PluginManager.__instance['plugin_cache'], dict):
            PluginManager.__instance['plugin_cache'] = {}
        # Get the plugin cache path and create if needed
        cache_path = Config.get('path/plugin_cache')
        os.makedirs(cache_path, exist_ok=True)
        # Open or clone the plugins repository with the plugin cache path
        cache = GitManager.open_or_clone(cache_path + os.sep + PluginManager.DEFAULT_BARE_REPO_PATH, Config.get('plugins/url', PluginManager.DEFAULT_CACHE_URL), bare=True)
        if cache is None:
            # Log that loading the plugin cache information failed
            Logger.warning(f'MEG Plugins: Could not update plugin cache information')
            return False
        try:
            # Log updating plugin cache information
            Logger.debug(f'MEG Plugins: Fetching plugin cache information')
            # Fetch and update the plugin cache
            cache.fetch_all()
            fetch_head = cache.lookup_reference('FETCH_HEAD')
            if fetch_head is not None:
                cache.head.set_target(fetch_head.target)
            # Checkout the plugin information files
            cache.checkout_head(directory=cache_path, paths=['*/' + PluginInformation.DEFAULT_PLUGIN_INFO_PATH])
        except Exception as e:
            # Log that loading the plugin cache information failed
            Logger.warning(f'MEG Plugins: {e}')
            Logger.warning(f'MEG Plugins: Could not update plugin cache information')
            return False
        # Log updating plugin cache information
        Logger.debug(f'MEG Plugins: Updating plugin cache information')
        # Obtain the available plugins from the plugin cache path
        retval = True
        for (path, dirs, files) in os.walk(cache_path):
            # For each available plugin load the information
            for d in dirs:
                # Ignore the repository index in the cache
                if d == PluginManager.DEFAULT_BARE_REPO_PATH:
                    continue
                # Log debug information about the available plugin
                plugin_path = path + os.sep + d
                Logger.debug(f'MEG Plugins: Found plugin cache information <{plugin_path}>')
                try:
                    # Get the available plugin path and load plugin information
                    plugin = PluginInformation(plugin_path)
                    # Log plugin information
                    PluginManager._log_plugin(plugin)
                    # Add the plugin information to the cache
                    PluginManager.__instance['plugin_cache'][plugin.name()] = plugin
                except Exception as e:
                    # Log that loading the plugin cache information failed
                    Logger.warning(f'MEG Plugins: {e}')
                    Logger.warning(f'MEG Plugins: Could not load information for plugin cache <{plugin_path}>')
                    retval = False
            # Do not actually walk the directory tree, only get directories directly under plugin cache path
            break
        # Update the plugin information, if needed
        if retval and update:
            retval = PluginManager.update()
        return retval

    # Install plugin by name
    @staticmethod
    def install(name, force=False):
        """Install plugin by name"""
        # Log installing plugin
        Logger.debug(f'MEG Plugins: Installing plugin <{name}>')
        # Get the available plugin by name
        available_plugin = PluginManager.get_available(name)
        if available_plugin is None:
            # Log failed to install plugin
            Logger.warning(f'MEG Plugins: Failed to install plugin <{name}>')
            return False
        # Log updating plugin cache information
        Logger.debug(f'MEG Plugins: Found plugin cache information <{available_plugin.path()}>')
        PluginManager._log_plugin(available_plugin)
        # Get installed plugin by name, if present
        plugin = PluginManager.get(name)
        if plugin is not None:
            # Check plugin is up to date or forcing installation
            if available_plugin.compare_versions(plugin) <= 0 and not force:
                return True
        # Get the plugins cache path
        plugins_path = Config.get('path/plugins')
        # Get the plugin installation path
        plugin_basename = os.path.basename(available_plugin.path())
        plugin_path = plugins_path + os.sep + plugin_basename
        try:
            # Remove the previous plugin path, if necessary
            if os.path.exists(plugin_path):
                if os.path.isdir(plugin_path):
                    # Remove plugin directory
                    shutil.rmtree(plugin_path)
                else:
                    # Remove plugin directory block file
                    os.remove(plugin_path)
            # Open the local plugin cache repository
            cache_path = Config.get('path/plugin_cache') + os.sep + '.git'
            cache = GitManager.open(cache_path, bare=True)
            if cache is None:
                raise GitException(f'Could not open local plugin cache <{cache_path}>')
            # Log installing plugin
            Logger.debug(f'MEG Plugins: Installing plugin <{plugin_path}>')
            # Install plugin by checking out
            cache.checkout_head(directory=plugins_path, paths=[plugin_basename + '/*'])
            # Load (or update) plugin information
            plugin = PluginManager._update(plugin_path)
            if plugin is not None:
                # Log plugin information
                PluginManager._log_plugin(plugin)
                # Setup plugin dependencies
                plugin.setup().check_returncode()
                # Add the plugin
                PluginManager.__instance['plugins'][plugin.name()] = plugin
        except Exception as e:
            # Log that loading the plugin cache information failed
            Logger.warning(f'MEG Plugins: {e}')
            Logger.warning(f'MEG Plugins: Could not load information for plugin <{plugin_path}>')
            return False
        return True

    # TODO: Install plugin from local path

    # Uninstall plugin by name
    @staticmethod
    def uninstall(name):
        """Uninstall plugin by name"""
        # Log uninstalling plugin
        Logger.debug(f'MEG Plugins: Uninstalling plugin <{name}>')
        # Get the plugin by name
        plugin = PluginManager.get(name)
        if plugin is not None:
            try:
                # Disable (and unload) the plugin, if needed
                plugin.disable()
                # Remove the plugin instance
                PluginManager.__instance['plugins'].pop(name)
                # Remove the plugin directory
                shutil.rmtree(plugin.path())
            except Exception as e:
                # Log uninstalling plugin failed
                Logger.warning(f'MEG Plugins: {e}')
                Logger.warning(f'MEG Plugins: Failed to uninstall plugin <{name}>')
                return False
        return True

    # Get the current plugin information (from a plugin)
    @staticmethod
    def get_current(obj=None):
        """Get the current plugin information (from a plugin)"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager()
        if PluginManager.__instance is None:
            return None
        # Check if trying to match a specific object to a plugin
        if obj is not None:
            try:
                # Check each plugin for a matching module package
                for plugin in PluginManager.get_all():
                    # Check if the plugin has a module loaded and if the name is the same as the object module
                    if 'module' in plugin and plugin['module'].__name__ == sys.modules[obj.__module__].__package__:
                        # Found the current plugin
                        return plugin
            except Exception:
                # There was a problem determining the object module
                return None
        else:
            try:
                # Get the current call frame (this function)
                frames = list(sys._current_frames().values())
                frame = frames[len(frames) - 1]
                # Walk back up the call stack until there are no frames or a matching module is found
                while frame.f_back is not None:
                    # Get the previous call frame
                    frame = frame.f_back
                    # Check each plugin for a matching module
                    for plugin in PluginManager.get_all():
                        # Check if the plugin has a module loaded and if the name is the same as the call frame module
                        if 'module' in plugin and plugin['module'].__name__ == frame.f_globals['__package__']:
                            # Found the current plugin
                            return plugin
            except Exception:
                # There was a problem walking the call stack
                return None
        # The current plugin was not found (probably because this function was not called from a plugin)
        return None

    # Get available plugin information by name
    @staticmethod
    def get_available(name):
        """Get available plugin information by name"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager()
        if PluginManager.__instance is not None and 'plugin_cache' in PluginManager.__instance:
            if name in PluginManager.__instance['plugin_cache']:
                return PluginManager.__instance['plugin_cache'][name]
        return None

    # Get all available plugins information
    @staticmethod
    def get_all_available():
        """Get all available plugins information"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager()
        if PluginManager.__instance is None or 'plugin_cache' not in PluginManager.__instance:
            return []
        return PluginManager.__instance['plugin_cache'].values()

    # Get all available plugin names
    @staticmethod
    def get_available_names():
        """Get all available plugin names"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager()
        if PluginManager.__instance is None or 'plugin_cache' not in PluginManager.__instance:
            return []
        return PluginManager.__instance['plugin_cache'].keys()

    # Get plugin by name
    @staticmethod
    def get(name):
        """Get plugin by name"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager()
        if PluginManager.__instance is not None and 'plugins' in PluginManager.__instance:
            if name in PluginManager.__instance['plugins']:
                return PluginManager.__instance['plugins'][name]
        return None

    # Get all plugins
    @staticmethod
    def get_all():
        """Get all plugins"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager()
        if PluginManager.__instance is None or 'plugins' not in PluginManager.__instance:
            return []
        return PluginManager.__instance['plugins'].values()

    # Get all plugin names
    @staticmethod
    def get_names():
        """Get all plugin names"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager()
        if PluginManager.__instance is None or 'plugins' not in PluginManager.__instance:
            return []
        return PluginManager.__instance['plugins'].keys()

    # Enable plugin by name
    @staticmethod
    def enable(name):
        """Enable plugin by name"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager()
        if PluginManager.__instance is None:
            return False
        # Get the plugin by name
        plugin = PluginManager.get(name)
        # Check if the plugin was found
        if plugin is None:
            return False
        if not plugin.enabled():
            try:
                # Log debug information about the plugin
                Logger.debug(f'MEG Plugins: Enabling plugin <{name}>')
                # Enable the plugin
                plugin.enable()
            except Exception as e:
                # Log that enabling the plugin failed
                Logger.warning(f'MEG Plugins: {e}')
                Logger.warning(f'MEG Plugins: Could not enable plugin <{name}>')
                return False
        return True

    # Enable all plugins
    @staticmethod
    def enable_all():
        """Enable all plugins"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager()
        if PluginManager.__instance is None:
            return False
        retval = True
        # For each plugin, enable the plugin
        for name in PluginManager.get_names():
            retval = PluginManager.enable(name) and retval
        return retval

    # Disable plugin by name
    @staticmethod
    def disable(name):
        """Disable plugin by name"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager()
        if PluginManager.__instance is None:
            return False
        try:
            # Get the plugin by name
            plugin = PluginManager.get(name)
            # Check if the plugin was found
            if plugin is not None and plugin.enabled():
                # Log debug information about the plugin
                Logger.debug(f'MEG Plugins: Disabling plugin <{name}>')
                # Disable the plugin
                plugin.disable()
        except Exception as e:
            # Log that disabling the plugin failed
            Logger.warning(f'MEG Plugins: {e}')
            Logger.warning(f'MEG Plugins: Could not disable plugin <{name}>')
            return False
        return True

    # Disable all plugins
    @staticmethod
    def disable_all():
        """Disable all plugins"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager()
        if PluginManager.__instance is None:
            return False
        retval = True
        # For each plugin, disable the plugin
        for name in PluginManager.get_names():
            retval = PluginManager.disable(name) and retval
        return retval

    # Setup plugin dependencies by name
    @staticmethod
    def setup(name):
        """Setup plugin dependencies by name"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager()
        if PluginManager.__instance is None:
            return False
        # Log debug information about the plugin
        Logger.debug(f'MEG Plugins: Setup dependencies for plugin <{name}>')
        # Get the plugin by name
        plugin = PluginManager.get(name)
        # Check if the plugin was found
        if plugin is None:
            return False
        try:
            # Setup the plugin dependencies
            plugin.setup().check_returncode()
        except Exception as e:
            # Log that setting up the plugin dependencies failed
            Logger.warning(f'MEG Plugins: {e}')
            Logger.warning(f'MEG Plugins: Could not setup dependencies for plugin <{name}>')
            return False
        return True

    # Setup all plugins dependencies
    @staticmethod
    def setup_all():
        """Setup all plugins dependencies"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager()
        if PluginManager.__instance is None:
            return False
        retval = True
        # For each plugin, setup the plugin dependencies
        for name in PluginManager.get_names():
            retval = PluginManager.setup(name) and retval
        return retval

    # Load plugin by name
    @staticmethod
    def load(name):
        """Load plugin by name"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager()
        if PluginManager.__instance is None:
            return False
        # Get the plugin by name
        plugin = PluginManager.get(name)
        if plugin is not None and not plugin.loaded():
            # Log debug information about the plugin
            Logger.debug(f'MEG Plugins: Found plugin <{plugin.path()}>')
            try:
                # Load the plugin
                plugin.load()
            except Exception as e:
                # Log that loading the plugin failed
                Logger.warning(f'MEG Plugins: {e}')
                Logger.warning(f'MEG Plugins: Could not load plugin <{plugin.path()}>')
                PluginManager.unload(name)
                return False
        return True

    # Load all plugins
    @staticmethod
    def load_all():
        """Load all plugins"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager()
        if PluginManager.__instance is None:
            return False
        retval = True
        # For each plugin, load the plugin
        for name in PluginManager.get_names():
            retval = PluginManager.load(name) and retval
        return retval

    # Load enabled plugins
    @staticmethod
    def load_enabled():
        """Load enabled plugins"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager()
        if PluginManager.__instance is None:
            return False
        # Get the enabled plugin names
        enabled_plugins = Config.get('plugins', [])
        if not isinstance(enabled_plugins, list):
            return False
        retval = True
        # For each enabled plugin, load the plugin
        for name in enabled_plugins:
            retval = PluginManager.load(name) and retval
        return retval

    # Unload plugin by name
    @staticmethod
    def unload(name):
        """Unload plugin by name"""
        # Get the plugin by name
        plugin = PluginManager.get(name)
        if plugin is not None and plugin.loaded():
            # Log debug information about the plugin
            Logger.debug(f'MEG Plugins: Unloading plugin <{plugin.path()}>')
            try:
                # Unload the plugin
                plugin.unload()
            except Exception as e:
                # Log that unloading the plugin failed
                Logger.warning(f'MEG Plugins: {e}')
                Logger.warning(f'MEG Plugins: Could not unload plugin <{plugin.path()}>')
                return False
        return True

    # Unload all plugins
    @staticmethod
    def unload_all():
        """Unload all plugins"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager()
        if PluginManager.__instance is None:
            return False
        retval = True
        # For each plugin, load the plugin
        for name in PluginManager.get_names():
            retval = PluginManager.unload(name) and retval
        return retval

    # Create plugin information from plugin path
    @staticmethod
    def _update(plugin_path):
        # Get the plugin path and load plugin information
        plugin = Plugin(plugin_path)
        # Check the plugin does not already exist by name
        current_plugin = PluginManager.get(plugin.name())
        if current_plugin is not None:
            # Determine higher version and keep that plugin
            comparison = Plugin.compare_versions(plugin, current_plugin)
            # The versions were equal so check if there are additional version fields
            if comparison == 0:
                # This plugin appears to be the same version so skip this one
                Logger.info(f'Plugin "{plugin.name()}" with version {plugin.version()} ignored because the same version already exists')
                plugin = None
            elif comparison < 0:
                # This plugin is older version than the previously loaded plugin so skip this one
                raise PluginException(f'Plugin "{plugin.name()}" with version {plugin.version()} ignored because newer version {current_plugin.version()} already exists')
            else:
                # This plugin is newer version than the previously loaded plugin so replace with this one
                Logger.info(f'MEG Plugins: Plugin "{plugin.name()}" with version {current_plugin.version()} replaced with newer version {plugin.version()}')
        # Return the created plugin information
        return plugin

    # Log plugin information from plugin
    @staticmethod
    def _log_plugin(plugin):
        # Log plugin information
        if isinstance(plugin, PluginInformation):
            Logger.debug(f"MEG Plugins:   Name:    {plugin.name()}")
            Logger.debug(f"MEG Plugins:   Version: {plugin.version()}")
            Logger.debug(f"MEG Plugins:   Author:  {plugin.author()} <{plugin.email()}>")
            Logger.debug(f"MEG Plugins:   Brief:   {plugin.brief()}")
