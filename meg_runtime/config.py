"""Multimedia Extensible Git (MEG) configuration

Configuration for runtime
"""

import os
import re
import json
from pathlib import Path
from kivy.logger import Logger


# Runtime configuration
class Config(dict):
    """Runtime configuration"""

    # The singleton configuration instance
    __instance = None

    # Configuration constructor
    def __init__(self, **kwargs):
        """Configuration constructor"""
        # Check if there is already a configuration instance
        if Config.__instance is not None:
            # Except if another instance is created
            raise Exception(self.__class__.__name__ + " is a singleton!")
        else:
            # Initialize super class constructor
            super().__init__(**kwargs)
            # Set this as the current configuration instance
            Config.__instance = self
            # Load the default configuation values
            Config.clear()

    # Load a configuration from file
    @staticmethod
    def load(path):
        """Load a configuration from file"""
        # Check there is a configuration instance
        if Config.__instance is None:
            Config()
        if Config.__instance is not None:
            # Clear the old configuration before loading a new one
            Config.clear()
            try:
                # Get the configuration path
                expanded_path = Config.expand(path)
                Logger.debug(f'MEG Config: Loading configuration <{expanded_path}>')
                # Try to open the configuration file for reading
                config_file = open(expanded_path, "r")
                # Try to parse the JSON configuration file
                config = json.load(config_file)
                # Overwrite or update the configuration
                Config.__instance.update(config)
            except Exception as e:
                # Log that loading the configuration failed
                Logger.warning(f'MEG Config: {e}')
                Logger.warning(f'MEG Config: Could not load configuration <{expanded_path}>')

    # Save a configuration to file
    @staticmethod
    def save(path, overwrite=True):
        """Save a configuration to JSON file"""
        # Check there is a configuration instance
        if Config.__instance is None:
            Config()
        if Config.__instance is not None:
            try:
                Logger.debug(f'MEG Config: Saving configuration <{Config.expand(path)}>')
                # Check the file exists before overwriting
                if not overwrite and os.path.exists(path):
                    raise Exception(f'Not overwriting existing file <{path}>')
                # Try to open the configuration file for writing
                config_file = open(path, "w")
                # Try to convert configuration to JSON file
                json.dump(Config.__instance, config_file)
            except Exception as e:
                # Log that saving the configuration failed
                Logger.warning(f'MEG Config: {e}')
                Logger.warning(f'MEG Config: Could not save configuration <{Config.expand(path)}>')

    # Expand a configuration value with configuration references
    @staticmethod
    def expand(value, keys=[]):
        """Expand a configuration value with configuration references"""
        # Only expand strings
        if isinstance(value, str):
            # Replace any dictionary references
            matches = re.findall('[$][(]([^)]+)[)]', value, re.I+re.S)
            if matches is not None:
                # Remove any duplicates from matches
                matches = list(dict.fromkeys(matches))
                # Replace each dictionary references
                for m in matches:
                    # Replace the dictionary reference with the value
                    m_stripped = m.strip()
                    value = value.replace('$(' + m + ')', '' if m_stripped in keys else Config.get(m_stripped, keys=keys))
        # Return original value or expanded configuration value
        return value

    # Get a configuration value
    @staticmethod
    def get(key, defaultValue='', keys=[]):
        """Get a configuration value"""
        # Check the configuration dictionary is valid
        if Config.__instance is None:
            Config()
        if not isinstance(key, str) or Config.__instance is None:
            return defaultValue
        # Check the key is in the configuration dictionary by splitting into individual parts
        current_dict = Config.__instance
        subkeys = key.split('/')
        # Go through each key and traverse the configuration dictionary
        for sk in subkeys:
            # Check current key is in current dictionary
            if sk not in current_dict:
                return defaultValue
            # Get the dictionary element by key
            current_dict = current_dict[sk]
        # Add the key to the keys list to prevent recursion
        if isinstance(keys, list):
            expanded_keys = keys.copy()
        else:
            expanded_keys = []
        if key not in expanded_keys:
            expanded_keys.append(key)
        # Return the (possibly expanded) dictionary element
        return Config.expand(current_dict, expanded_keys)

    # Check a configuration key exists
    @staticmethod
    def exists(key):
        """Check a configuration key exists"""
        # Check the configuration dictionary is valid
        if Config.__instance is None:
            Config()
        if not isinstance(key, str) or Config.__instance is None:
            return False
        # Check the key is in the configuration dictionary by splitting into individual parts
        current_dict = Config.__instance
        subkeys = key.split('/')
        # Go through each key and traverse the configuration dictionary
        for sk in subkeys:
            # Check current key is in current dictionary
            if sk not in current_dict:
                return False
            # Get the dictionary element by key
            current_dict = current_dict[sk]
        # Key was found in configuration
        return True

    # Set a configuration value
    @staticmethod
    def set(key, value):
        """Set a configuration value"""
        # Check the configuration dictionary is valid
        if Config.__instance is None:
            Config()
        if isinstance(key, str) and Config.__instance is not None:
            # Check the value is valid or remove the key
            if value is None:
                # Remove the key if the value is invalid
                Config.remove(key)
            else:
                # Check the key is in the configuration dictionary by splitting into individual parts
                current_dict = Config.__instance
                keys = key.split('/')
                # Go through each key and traverse the configuration dictionary
                for k in keys[:-1]:
                    # Check current key is in current dictionary
                    if k not in current_dict:
                        current_dict[k] = {}
                    # Get the dictionary element by key
                    current_dict = current_dict[k]
                # Set the dictionary element value
                current_dict[keys[-1]] = value

    # Remove a configuration value
    @staticmethod
    def remove(key):
        """Remove a configuration value"""
        # Check the configuration dictionary is valid
        if Config.__instance is None:
            Config()
        if isinstance(key, str) and Config.__instance is not None:
            # Check the key is in the configuration dictionary by splitting into individual parts
            current_dict = Config.__instance
            keys = key.split('/')
            # Go through each key and traverse the configuration dictionary
            for k in keys[:-1]:
                # Check current key is in current dictionary
                if k not in current_dict:
                    return
                # Get the dictionary element by key
                current_dict = current_dict[k]
            # Remove the dictionary element
            k = keys[-1]
            if k in current_dict:
                current_dict.pop(k)

    # Clear the configuration
    @staticmethod
    def clear():
        """Clear the configuration"""
        # Check the configuration dictionary is valid
        if Config.__instance is None:
            Config()
        else:
            # Do not recreate default values because the constructor will set them
            if Config.__instance is not None:
                # Clear the dictionary
                super(Config, Config.__instance).clear()
            # Get the user path from the environment, if present, otherwise use the default path
            if 'MEG_USER_PATH' in os.environ:
                Config.set('path/user', os.environ['MEG_USER_PATH'])
            else:
                Config.set('path/user', str(Path.home()))
            # Get the home path from the environment, if present, otherwise use the default path
            if 'MEG_HOME_PATH' in os.environ:
                Config.set('path/home', os.environ['MEG_HOME_PATH'])
            else:
                Config.set('path/home', '$(path/user)' + os.sep + '.meg')
            # Get the cache path from the environment, if present, otherwise use the default path
            if 'MEG_CACHE_PATH' in os.environ:
                Config.set('path/cache', os.environ['MEG_CACHE_PATH'])
            else:
                Config.set('path/cache', '$(path/home)' + os.sep + 'cache')
            # Get the plugins path from the environment, if present, otherwise use the default path
            if 'MEG_PLUGINS_PATH' in os.environ:
                Config.set('path/plugins', os.environ['MEG_PLUGINS_PATH'])
            else:
                Config.set('path/plugins', '$(path/home)' + os.sep + 'plugins')
            # Get the plugin cache path from the environment, if present, otherwise use the default path
            if 'MEG_PLUGIN_CACHE_PATH' in os.environ:
                Config.set('path/plugin_cache', os.environ['MEG_PLUGIN_CACHE_PATH'])
            else:
                Config.set('path/plugin_cache', '$(path/home)' + os.sep + 'plugin_cache')
            # Load configuration from the environment, if present, otherwise use the default path
            if 'MEG_CONFIG_PATH' in os.environ:
                Config.set('path/config', os.environ['MEG_CONFIG_PATH'])
            else:
                Config.set('path/config', '$(path/home)' + os.sep + 'config.json')
