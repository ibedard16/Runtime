"""Multimedia Extensible Git (MEG) plugin extension

Plugin extension for runtime
"""

import os
import sys
import json
import inspect
import importlib
import subprocess
from kivy.logger import Logger
from meg_runtime.config import Config


# Runtime plugin exception
class PluginException(Exception):
    """Runtime plugin exception"""

    # Plugin exception constructor
    def __init__(self, message, **kwargs):
        """Plugin exception constructor"""
        super().__init__(message, **kwargs)


# Runtime plugin extension information
class PluginInformation(dict):
    """Runtime plugin extension information"""

    # The default plugin information path
    DEFAULT_PLUGIN_INFO_PATH = 'plugin.json'
    # The default plugin script path
    DEFAULT_PLUGIN_SCRIPT_PATH = '__init__.py'

    # The required plugin information fields
    __fields = {
        'name': str,
        'version': str,
        'author': str,
        'email': str,
        'brief': str,
        'description': str,
        'dependencies': list
    }

    # Plugin information constructor
    def __init__(self, plugin_path, **kwargs):
        """Plugin information constructor"""
        # Initialize super class constructor
        super().__init__(**kwargs)
        # Get the plugin information file path
        plugin_info_path = plugin_path + os.sep + PluginInformation.DEFAULT_PLUGIN_INFO_PATH
        # Try to load plugin information
        plugin_info_file = open(plugin_info_path, 'r')
        # Log debug information about the plugin
        Logger.debug(f'MEG Plugins: Loading information for plugin <{plugin_info_path}>')
        # Load plugin information
        plugin_info = json.load(plugin_info_file)
        # Validate plugin information
        if plugin_info is not None:
            for field in PluginInformation.__fields:
                if field not in plugin_info:
                    raise PluginException(f'Missing required field "{field}" for plugin information <{plugin_info_path}>')
                if not isinstance(plugin_info[field], PluginInformation.__fields[field]):
                    raise PluginException(f'Invalid required field "{field}" for plugin information <{plugin_info_path}>')
            for field in plugin_info:
                if field not in PluginInformation.__fields:
                    raise PluginException(f'Unknown field "{field}" for plugin information <{plugin_info_path}>')
            # Set plugin information
            self.update(plugin_info)
            self['info'] = plugin_info_path
            self['path'] = plugin_path

    # Compare version with another plugin information
    def compare_versions(self, plugin):
        """Compare version with another plugin information"""
        # Check that the comparison is valid
        if not isinstance(self, PluginInformation) or not isinstance(plugin, PluginInformation):
            raise PluginException(f'Cannot compare versions of non plugin types <{self.__class__.__name__}, {plugin.__class__.__name__}>')
        # Determine higher version
        version1 = self.version().split('.')
        version2 = plugin.version().split('.')
        length1 = len(version1)
        length2 = len(version2)
        for i in range(min(length1, length2)):
            i_version1 = int(version1[i])
            i_version2 = int(version2[i])
            if i_version1 != i_version2:
                return i_version1 - i_version2
        # The versions were equal to the mininum length so check if there are additional version fields
        return length1 - length2

    # Get plugin path
    def path(self):
        """Get plugin path"""
        if 'path' not in self or not isinstance(self['path'], str):
            return ''
        return self['path']

    # Get plugin script path
    def script(self):
        """Get plugin script path"""
        if 'script' not in self or not isinstance(self['script'], str):
            return self.path() + os.sep + PluginInformation.DEFAULT_PLUGIN_SCRIPT_PATH
        return self['script']

    # Get plugin name
    def name(self):
        """Get plugin name"""
        if 'name' not in self or not isinstance(self['name'], Plugin.__fields['name']):
            return ''
        return self['name']

    # Get plugin version
    def version(self):
        """Get plugin version"""
        if 'version' not in self or not isinstance(self['version'], Plugin.__fields['version']):
            return ''
        return self['version']

    # Get plugin author
    def author(self):
        """Get plugin author"""
        if 'author' not in self or not isinstance(self['author'], Plugin.__fields['author']):
            return ''
        return self['author']

    # Get plugin email
    def email(self):
        """Get plugin email"""
        if 'email' not in self or not isinstance(self['email'], Plugin.__fields['email']):
            return ''
        return self['email']

    # Get plugin brief
    def brief(self):
        """Get plugin brief"""
        if 'brief' not in self or not isinstance(self['brief'], Plugin.__fields['brief']):
            return ''
        return self['brief']

    # Get plugin description
    def description(self):
        """Get plugin description"""
        if 'description' not in self or not isinstance(self['description'], Plugin.__fields['description']):
            return ''
        return self['description']

    # Get plugin dependencies
    def dependencies(self):
        """Get plugin dependencies"""
        if 'dependencies' not in self or not isinstance(self['dependencies'], Plugin.__fields['dependencies']):
            return []
        for dependency in self['dependencies']:
            if not isinstance(dependency, str):
                self['dependencies'].remove(dependency)
        return self['dependencies']


# Runtime plugin extension
class Plugin(PluginInformation):
    """Runtime plugin extension"""

    # Plugin constructor
    def __init__(self, plugin_path, **kwargs):
        """Plugin constructor"""
        # Initialize super class constructor
        super().__init__(plugin_path, **kwargs)

    # Plugin destructor
    def __del__(self):
        """Plugin destructor"""
        self.unload()

    # Enable the plugin
    def enable(self):
        """Enable the plugin"""
        # Get the enabled plugins
        enabled_plugins = Config.get('plugins', [])
        # Check if this plugin is already enabled
        if isinstance(enabled_plugins, list) and not self.name() in enabled_plugins:
            # Enable this plugin
            enabled_plugins.append(self.name())
            Config.set('plugins', enabled_plugins)

    # Disable the plugin
    def disable(self):
        """Disable the plugin"""
        # Get the enabled plugins
        enabled_plugins = Config.get('plugins', [])
        # Check if this plugin is already enabled
        if isinstance(enabled_plugins, list) and self.name() in enabled_plugins:
            # Disable this plugin
            enabled_plugins.remove(self.name())
            Config.set('plugins', enabled_plugins)
            # Unload plugin
            self.unload()

    # Setup the plugin dependencies
    def setup(self):
        """Install the plugin dependencies"""
        # Setup plugin dependencies
        depends = self.dependencies()
        if isinstance(depends, list) and len(depends) > 0:
            # Execute PIP to install the dependencies
            if os.name == 'nt':
                cmd = ['py', '-3']
            else:
                cmd = ['python3']
            cmd.extend(['-m', 'pip', 'install', '--target', Config.get('path/cache'), '--upgrade'])
            cmd.extend(depends)
            return subprocess.run(cmd, encoding='utf-8', stdin=None, stdout=subprocess.PIPE, stderr=None, startupinfo=subprocess.STARTUPINFO(wShowWindow=False))
        # No dependencies so return success status
        return subprocess.CompletedProcess([], 0)

    # Load the plugin
    def load(self):
        """Load the plugin"""
        if not self.loaded():
            # Log debug information about the plugin
            Logger.debug(f'MEG Plugins: Loading plugin script <{self.script()}>')
            # Try to load plugin
            plugin_spec = importlib.util.spec_from_file_location(os.path.basename(self.path()), self.script())
            if plugin_spec is not None:
                plugin_module = importlib.util.module_from_spec(plugin_spec)
                if plugin_module is not None:
                    # Set plugin module
                    self['spec'] = plugin_spec
                    self['module'] = plugin_module
                    # Add the plugin path to the system path
                    sys.path.append(self.path())
                    # Execute the plugin module
                    sys.modules[plugin_spec.name] = plugin_module
                    plugin_spec.loader.exec_module(plugin_module)

    # Unload the plugin, if loaded
    def unload(self):
        """Unload the plugin, if loaded"""
        # Delete the self reference to the module
        if 'module' in self:
            # Remove all modules imported by module
            for (name, module) in list(filter(lambda x: inspect.ismodule(x[1]), inspect.getmembers(self['module']))):
                if name in sys.modules:
                    del sys.modules[name]
            # Delete the module self reference
            del self['module']
        # Delete the module
        if 'spec' in self:
            # Remove the module
            if self['spec'].name is not None and self['spec'].name in sys.modules:
                del sys.modules[self['spec'].name]
            # Delete the module spec
            del self['spec']
        # Remove the plugin path from sys path
        if sys.path is not None and self.path() in sys.path:
            sys.path.remove(self.path())

    # Get if plugin is enabled
    def enabled(self):
        """Get if plugin is enabled"""
        # Check if plugin is enabled
        enabled_plugins = Config.get('plugins', [])
        return isinstance(enabled_plugins, list) and self.name() in enabled_plugins

    # Get if plugin is loaded
    def loaded(self):
        """Get if plugin is loaded"""
        # Check if plugin is loaded
        return 'module' in self and 'spec' in self and self['spec'].name is not None and self['spec'].name in sys.modules
