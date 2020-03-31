"""Multimedia Extensible Git (MEG) plugin manager

Plugin manager for runtime
"""

import os
import re
import sys
import errno
import shutil
import tarfile
import zipfile
from kivy.logger import Logger
from meg_runtime.config import Config
from meg_runtime.plugins import Plugin, PluginInformation, PluginException
from meg_runtime.git import GitException, GitManager


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
            # Set plugin and cache paths in python path for import
            sys.path.append(Config.get('path/plugins'))
            sys.path.append(Config.get('path/cache'))
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
        Logger.debug(f'MEG Plugins: Updating plugin information {Config.get("path/plugins")}')
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
                plugin_path = os.path.join(path, d)
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
                    # Do not say there was an error if the file does not exists
                    if e.errno != errno.ENOENT:
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
        cache_path = os.path.join(Config.get('path/plugin_cache'), 'remote')
        os.makedirs(cache_path, exist_ok=True)
        # Open or clone the plugins repository with the plugin cache path
        cache = GitManager.open_or_clone(os.path.join(cache_path, PluginManager.DEFAULT_BARE_REPO_PATH), Config.get('plugins/url', PluginManager.DEFAULT_CACHE_URL), bare=True)
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
        return PluginManager._update_cache(cache_path, update)

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
        plugin_path = os.path.join(plugins_path, plugin_basename)
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
            cache_path = os.path.join(Config.get('path/plugin_cache'), 'remote', PluginManager.DEFAULT_BARE_REPO_PATH)
            cache = GitManager.open(cache_path, bare=True)
            if cache is None:
                raise GitException(f'Could not open local plugin cache <{cache_path}>')
            # Log installing plugin
            Logger.debug(f'MEG Plugins: Installing plugin <{plugin_path}>')
            # Install plugin by checking out
            cache.checkout_head(directory=plugins_path, paths=[plugin_basename + '/*'])
            # Load (or update) plugin information
            plugin = PluginManager._update(plugin_path, force)
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

    # Install plugin from local path
    @staticmethod
    def install_path(path, force=False):
        """Install plugin from local path"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager()
        if PluginManager.__instance is None:
            return False
        # Check if path does not exist
        if not os.path.exists(path) or not os.path.isdir(path):
            return False
        # Log trying to load plugin information from path
        Logger.debug(f'MEG Plugins: Installing plugin from path <{path}>')
        try:
            # Get the plugin information for the path if no other version is installed
            plugin = PluginManager._update(path, force)
            if plugin is None:
                # The same version exists and no force so this is installed
                return True
            # Log plugin information
            PluginManager._log_plugin(plugin)
            # Log trying to load plugin information from path
            Logger.debug(f'MEG Plugins: Installing plugin <{plugin.name()}>')
            # Get the installed plugin path
            plugin_path = os.path.join(Config.get('path/plugins'), os.path.basename(path))
            # Remove the previous plugin path, if necessary
            if os.path.exists(plugin_path):
                if os.path.isdir(plugin_path):
                    # Remove plugin directory
                    shutil.rmtree(plugin_path)
                else:
                    # Remove plugin directory block file
                    os.remove(plugin_path)
            # Copy the path to the plugins directory
            shutil.copytree(path, plugin_path)
            # Load (or update) plugin information
            plugin = Plugin(plugin_path)
            if plugin is not None:
                # Log plugin information
                PluginManager._log_plugin(plugin)
                # Setup plugin dependencies
                plugin.setup().check_returncode()
                # Add the plugin
                PluginManager.__instance['plugins'][plugin.name()] = plugin
        except Exception as e:
            # Log that installing the plugin from the path failed
            Logger.warning(f'MEG Plugins: {e}')
            Logger.warning(f'MEG Plugins: Failed to install plugin from path <{path}>')
            return False
        return True

    # Install plugin archive
    @staticmethod
    def install_archive(path, force=False):
        """Install plugin archive"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager()
        if PluginManager.__instance is None:
            return False
        # Check if path does not exist
        if os.path.exists(path):
            # Log trying to load plugin information from archive
            Logger.debug(f'MEG Plugins: Installing plugin(s) from archive <{path}>')
            try:
                # Check if zip file plugin
                archive = zipfile.ZipFile(path)
                # Get the archive list for the found plugins
                return PluginManager._install_archive_zip(archive, os.path.splitext(os.path.basename(path))[0], force)
            except zipfile.BadZipFile:
                try:
                    # Check if tar file plugin
                    archive = tarfile.open(path)
                    # Get the archive list for the found plugins
                    return PluginManager._install_archive_tar(archive, os.path.splitext(os.path.basename(path))[0], force)
                except Exception as e:
                    # Log exception
                    Logger.warning(f'MEG Plugins: {e}')
            except Exception as e:
                # Log exception
                Logger.warning(f'MEG Plugins: {e}')
        # Log that installing the plugin information from archive failed
        Logger.warning(f'MEG Plugins: Could not install plugin(s) from archive <{path}>')
        return False

    # Install plugin archive from url
    @staticmethod
    def install_archive_from_url(url, force=False):
        """Install plugin archive from url"""
        # Check there is plugin manager instance
        if PluginManager.__instance is None:
            PluginManager()
        if PluginManager.__instance is None:
            return False
        # Download archive
        archive_path = Config.download(url)
        if not archive_path:
            return False
        # Install from downloaded archive
        return PluginManager.install_archive(archive_path, force)

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
        try:
            # Check if trying to match a specific object to a plugin
            if obj is not None:
                # Get the current plugin from the object
                return PluginManager._get_current_from(obj)
            # Get the current plugin from the call stack
            return PluginManager._get_current()
        except Exception:
            # There was a problem walking the call stack
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
    def _update(plugin_path, force=False):
        """Create plugin information from plugin path"""
        # Get the plugin path and load plugin information
        plugin = Plugin(plugin_path)
        # If forcing do not bother checking new version
        if not force:
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
        """Log plugin information from plugin"""
        # Log plugin information
        if isinstance(plugin, PluginInformation):
            Logger.debug(f"MEG Plugins:   Name:    {plugin.name()}")
            Logger.debug(f"MEG Plugins:   Version: {plugin.version()}")
            Logger.debug(f"MEG Plugins:   Author:  {plugin.author()} <{plugin.email()}>")
            Logger.debug(f"MEG Plugins:   Brief:   {plugin.brief()}")

    # Update plugin cache information
    @staticmethod
    def _update_cache(cache_path, update):
        """Update plugin cache information"""
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
                plugin_path = os.path.join(path, d)
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

    # Install plugin from archive list
    @staticmethod
    def _install_archive_list(archive, archive_list, force):
        """Install plugin from archive list"""
        # Get the plugin cache path and create if needed
        plugins_path = os.path.join(Config.get('path/plugin_cache'), 'local')
        os.makedirs(plugins_path, exist_ok=True)
        # Extract found plugins from archive to install
        retval = True
        for plugin_name, plugin_list in archive_list:
            # Get the plugin path
            plugin_path = os.path.join(plugins_path, plugin_name)
            # Log caching plugin
            Logger.debug(f'MEG Plugins: Locally caching plugin <{plugin_path}>')
            try:
                # Remove the previous plugin path, if necessary
                if os.path.exists(plugin_path):
                    if os.path.isdir(plugin_path):
                        # Remove plugin directory
                        shutil.rmtree(plugin_path)
                    else:
                        # Remove plugin directory block file
                        os.remove(plugin_path)
                # Extract each plugin from archive to install
                archive.extractall(plugin_path, plugin_list)
                # Install cached plugin
                retval = PluginManager.install_path(plugin_path, force) and retval
            except Exception as e:
                # Log that caching plugin locally failed
                Logger.warning(f'MEG Plugins: {e}')
                Logger.warning(f'MEG Plugins: Failed to locally cache plugin <{plugin_path}>')
                retval = False
        return retval

    # Install plugin from zip archive
    @staticmethod
    def _install_archive_zip(archive, base_name, force):
        """Install plugin from zip archive"""
        # Get the archive paths info list
        path_list = archive.infolist()
        # Check if archive is plugin
        if Plugin.DEFAULT_PLUGIN_INFO_PATH in path_list:
            # Archive is bare plugin
            archive_list = [(base_name, path_list)]
        else:
            # Check if plugin(s) information is in archive
            archive_list = []
            # Create a regex to match plugin information paths
            path_re = re.compile(r'((.*/)?([^/]+)/)' + re.escape(Plugin.DEFAULT_PLUGIN_INFO_PATH))
            # Add the base names of plugins to a list
            base_names = []
            for archive_path in path_list:
                # Check if there is a matching plugin configuration
                m = path_re.match(archive_path.filename)
                if m:
                    # Append the base name of the plugin
                    base_names.append(m.group(3, 1))
            # Create the plugin archive list for each found plugin information
            if len(base_names) > 0:
                for base_name, base_path in base_names:
                    # Create the plugin archive list
                    valid = False
                    plugin_list = []
                    # Create a regex to match plugin and script paths
                    base_re = re.compile(re.escape(base_path) + r'.*')
                    script_re = re.compile(re.escape(base_path) + re.escape(Plugin.DEFAULT_PLUGIN_SCRIPT_PATH))
                    # Add all the plugin paths to the list
                    for archive_path in path_list:
                        # Check if the script path matches
                        if script_re.match(archive_path.filename):
                            valid = True
                        # Check if the plugin path matches
                        elif not base_re.match(archive_path.filename) or len(base_path) >= len(archive_path.filename):
                            continue
                        # Modify the path of the object to be relative to the plugin base path
                        archive_path.filename = archive_path.filename[len(base_path):]
                        # Append to the list if matched
                        plugin_list.append(archive_path)
                    # Add the plugin to the archive list if valid (has at least information and script)
                    if valid:
                        # Add the plugin to the archive list
                        archive_list.append((base_name, plugin_list))
        # Install plugin(s) information from archive
        return PluginManager._install_archive_list(archive, archive_list, force)

    # Install plugin from tar archive
    @staticmethod
    def _install_archive_tar(archive, base_name, force):
        """Install plugin from tar archive"""
        # Get the archive paths info list
        path_list = archive.getmembers()
        # Check if archive is plugin
        if Plugin.DEFAULT_PLUGIN_INFO_PATH in path_list:
            # Archive is bare plugin
            archive_list = [(base_name, path_list)]
        else:
            # Check if plugin(s) information is in archive
            archive_list = []
            # Create a regex to match plugin information paths
            path_re = re.compile(r'((.*/)?([^/]+)/)' + re.escape(Plugin.DEFAULT_PLUGIN_INFO_PATH))
            # Add the base names of plugins to a list
            base_names = []
            for archive_path in path_list:
                # Check if there is a matching plugin configuration
                m = path_re.match(archive_path.name)
                if m:
                    # Append the base name of the plugin
                    base_names.append(m.group(3, 1))
            # Create the plugin archive list for each found plugin information
            if len(base_names) > 0:
                for base_name, base_path in base_names:
                    # Create the plugin archive list
                    valid = False
                    plugin_list = []
                    # Create a regex to match plugin and script paths
                    base_re = re.compile(re.escape(base_path) + r'.*')
                    script_re = re.compile(re.escape(base_path) + re.escape(Plugin.DEFAULT_PLUGIN_SCRIPT_PATH))
                    # Add all the plugin paths to the list
                    for archive_path in path_list:
                        # Check if the script path matches
                        if script_re.match(archive_path.name):
                            valid = True
                        # Check if the plugin path matches
                        elif not base_re.match(archive_path.name) or len(base_path) >= len(archive_path.name):
                            continue
                        # Modify the path of the object to be relative to the plugin base path
                        archive_path.name = archive_path.name[len(base_path):]
                        # Append to the list if matched
                        plugin_list.append(archive_path)
                    # Add the plugin to the archive list if valid (has at least information and script)
                    if valid:
                        # Add the plugin to the archive list
                        archive_list.append((base_name, plugin_list))
        # Install plugin(s) information from archive
        return PluginManager._install_archive_list(archive, archive_list, force)

    # Get the current plugin information (from a plugin)
    @staticmethod
    def _get_current():
        """Get the current plugin information (from a plugin)"""
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
        # The current plugin was not found (probably because this function was not called from a plugin)
        return None

    # Get the current plugin information (from a plugin)
    @staticmethod
    def _get_current_from(obj):
        """Get the current plugin information (from a plugin)"""
        # Check each plugin for a matching module package
        for plugin in PluginManager.get_all():
            # Check if the plugin has a module loaded and if the name is the same as the object module
            if 'module' in plugin and plugin['module'].__name__ == sys.modules[obj.__module__].__package__:
                # Found the current plugin
                return plugin
        # The current plugin was not found (probably because this function was not called from a plugin)
        return None
