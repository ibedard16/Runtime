"""Multimedia Extensible Git (MEG) configuration

Configuration for runtime
"""

import os
import re
import json
import errno
import shutil
from pathlib import Path
from kivy.logger import Logger


# Runtime configuration exception
class ConfigException(Exception):
    """Runtime configuration exception"""

    # Runtime configuration exception constructor
    def __init__(self, message, **kwargs):
        """Runtime configuration exception constructor"""
        super().__init__(message, **kwargs)


# Runtime configuration
class Config(dict):
    """Runtime configuration"""

    # The singleton configuration instance
    __instance = None
    # The block list of keys to prevent setting
    __blocked_keys = [
        'path/config',
        'path/user'
    ]

    # Configuration constructor
    def __init__(self, **kwargs):
        """Configuration constructor"""
        # Check if there is already a configuration instance
        if Config.__instance is not None:
            # Except if another instance is created
            raise ConfigException(self.__class__.__name__ + " is a singleton!")
        else:
            # Initialize super class constructor
            super().__init__(**kwargs)
            # Set this as the current configuration instance
            Config.__instance = self
            # Load the default configuation values
            Config.clear()

    # Load a configuration from file
    @staticmethod
    def load(path='$(path/config)', clear=True):
        """Load a configuration from JSON file"""
        # Check there is a configuration instance
        if Config.__instance is None:
            Config()
        if Config.__instance is None:
            return False
        # Clear the old configuration before loading a new one, if wanted
        if clear:
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
            # Keep the correct path for configuration
            if 'path' not in Config.__instance or not isinstance(Config.__instance['path'], dict):
                Config.__instance._set_defaults()
            Config.__instance._set_required(expanded_path)
        except (OSError, IOError) as e:
            # Do not say there was an error if the file exists
            if e.errno == errno.ENOENT:
                return True
            raise e
        except Exception as e:
            # Log that loading the configuration failed
            Logger.warning(f'MEG Config: {e}')
            Logger.warning(f'MEG Config: Could not load configuration <{expanded_path}>')
            return False
        return True

    # Save a configuration to file
    @staticmethod
    def save(path='$(path/config)', overwrite=True):
        """Save a configuration to JSON file"""
        # Check there is a configuration instance
        if Config.__instance is None:
            Config()
        if Config.__instance is None:
            return False
        try:
            # Get the expanded path
            expanded_path = Config.expand(path)
            Logger.debug(f'MEG Config: Saving configuration <{expanded_path}>')
            # Check the file exists before overwriting
            if not overwrite and os.path.exists(expanded_path):
                raise ConfigException(f'Not overwriting existing file <{expanded_path}>')
            # Make the path to the containing directory if it does not exist
            dir_path = os.path.dirname(expanded_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            # Try to open the configuration file for writing
            config_file = open(expanded_path, "w")
            # Remove the blocked keys from being saved
            config_copy = Config.__instance.copy()
            for blocked_key in Config.__blocked_keys:
                Config.__instance._remove(config_copy, [sk for sk in blocked_key.split('/') if sk])
            # Try to convert configuration to JSON file
            json.dump(config_copy, config_file, indent=2)
        except Exception as e:
            # Log that saving the configuration failed
            Logger.warning(f'MEG Config: {e}')
            Logger.warning(f'MEG Config: Could not save configuration <{expanded_path}>')
            return False
        return True

    # Expand a configuration value with configuration references
    @staticmethod
    def expand(value, exclude_keys=[]):
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
                    value = value.replace('$(' + m + ')', '' if m_stripped in exclude_keys else Config.get(m_stripped, exclude_keys=exclude_keys))
        # Return original value or expanded configuration value
        return value

    # Get a configuration value
    @staticmethod
    def get(key, defaultValue='', exclude_keys=[]):
        """Get a configuration value"""
        # Check the configuration dictionary is valid
        if Config.__instance is None:
            Config()
        if not isinstance(key, str) or Config.__instance is None:
            return defaultValue
        # Check the key is in the configuration dictionary by splitting into individual parts
        current_dict = Config.__instance
        subkeys = [sk for sk in key.split('/') if sk]
        # Check to make sure the key was valid or return the default value
        if not len(subkeys) > 0:
            return defaultValue
        # Go through each key and traverse the configuration dictionary
        for sk in subkeys[:-1]:
            # Check current key is in current dictionary
            if sk not in current_dict:
                return defaultValue
            # Get the dictionary element by key
            current_dict = current_dict[sk]
            # Check the instance of the element is a dictionary or the key cannot be valid
            if not isinstance(current_dict, dict):
                return defaultValue
        # Get the value of the key
        sk = subkeys[-1]
        if sk not in current_dict:
            return defaultValue
        value = current_dict[sk]
        # Add the key to the exclude keys list to prevent recursion
        if isinstance(exclude_keys, list):
            expanded_keys = exclude_keys.copy()
        else:
            expanded_keys = []
        if key not in expanded_keys:
            expanded_keys.append(key)
        # Return the (possibly expanded) dictionary element
        return Config.expand(value, expanded_keys)

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
        subkeys = [sk for sk in key.split('/') if sk]
        # Check to make sure the key was valid
        if not len(subkeys) > 0:
            return False
        # Go through each key and traverse the configuration dictionary
        for sk in subkeys[:-1]:
            # Check current key is in current dictionary
            if sk not in current_dict:
                return False
            # Get the dictionary element by key
            current_dict = current_dict[sk]
            # Check the instance of the element is a dictionary or the key cannot be valid
            if not isinstance(current_dict, dict):
                return False
        # Key was found in configuration if in final dictionary
        return subkeys[-1] in current_dict

    # Set a configuration value
    @staticmethod
    def set(key, value):
        """Set a configuration value"""
        # Check the configuration dictionary is valid
        if Config.__instance is None:
            Config()
        if not isinstance(key, str) or Config.__instance is None:
            return False
        # Check the value is valid or remove the key
        if value is None:
            # Remove the key if the value is invalid
            return Config.remove(key)
        # Check the key is in the configuration dictionary by splitting into individual parts
        current_dict = Config.__instance
        subkeys = [sk for sk in key.split('/') if sk]
        # Check to make sure the key was valid or return the default value
        if not len(subkeys) > 0:
            return False
        # Check key is blocked
        if '/'.join(subkeys) in Config.__blocked_keys:
            return False
        # Go through each key and traverse the configuration dictionary
        for sk in subkeys[:-1]:
            # Check current key is in current dictionary
            if sk not in current_dict:
                current_dict[sk] = {}
            # Get the dictionary element by key
            current_dict = current_dict[sk]
            # Check the instance of the element is a dictionary or the key cannot be valid
            if not isinstance(current_dict, dict):
                return False
        # Set the dictionary element value
        current_dict[subkeys[-1]] = value
        return True

    # Remove a configuration value
    @staticmethod
    def remove(key):
        """Remove a configuration value"""
        # Check the configuration dictionary is valid
        if Config.__instance is None:
            Config()
        if not isinstance(key, str) or Config.__instance is None:
            return False
        # Check the key is in the configuration dictionary by splitting into individual parts
        current_dict = Config.__instance
        subkeys = [sk for sk in key.split('/') if sk]
        # Traverse the configuration dictionary to remove the key and empty parent dictionaries
        return Config.__instance._remove(Config.__instance, subkeys)

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
            # Set the default values
            Config.__instance._set_defaults()

    # Remove a key and all empty parent dictionaries that contain that key
    def _remove(self, current_dict, subkeys):
        # Check the subkeys are valid
        if not isinstance(subkeys, list) or not len(subkeys) > 0:
            return True
        # Check the dictionary is valid
        if not isinstance(current_dict, dict):
            return True
        # Get the current key
        sk = subkeys[0]
        # Check if this is the value to remove
        if len(subkeys) == 1:
            # Remove the key value
            current_dict.pop(sk)
        # Check if the subkey is in the current dictionary
        elif sk in current_dict:
            # Recurse the next subkey and dictionary
            self._remove(current_dict[sk], subkeys[1:])
            # Remove the dictionary if empty
            if not current_dict[sk]:
                current_dict.pop(sk)
        # Removed the key
        return True

    # Set the default values
    def _set_required(self, config_path):
        # Get the user path from the environment, if present, otherwise use the default path
        self['path']['user'] = str(Path.home()) if 'MEG_USER_PATH' not in os.environ else os.environ['MEG_USER_PATH']
        # Load configuration from the environment, if present, otherwise use the default path
        self['path']['config'] = config_path

    # Set the default values
    def _set_defaults(self):
        # Create the path dictionary
        self['path'] = {}
        # Set the required values
        self._set_required('$(path/home)' + os.sep + 'config.json' if 'MEG_CONFIG_PATH' not in os.environ else os.environ['MEG_CONFIG_PATH'])
        # Get the home path from the environment, if present, otherwise use the default path
        self['path']['home'] = '$(path/user)' + os.sep + '.meg' if 'MEG_HOME_PATH' not in os.environ else os.environ['MEG_HOME_PATH']
        # Get the cache path from the environment, if present, otherwise use the default path
        self['path']['cache'] = '$(path/home)' + os.sep + 'cache' if 'MEG_CACHE_PATH' not in os.environ else os.environ['MEG_CACHE_PATH']
        # Get the plugins path from the environment, if present, otherwise use the default path
        self['path']['plugins'] = '$(path/home)' + os.sep + 'plugins' if 'MEG_PLUGINS_PATH' not in os.environ else os.environ['MEG_PLUGINS_PATH']
        # Get the plugin cache path from the environment, if present, otherwise use the default path
        self['path']['plugin_cache'] = '$(path/home)' + os.sep + 'plugin_cache' if 'MEG_PLUGIN_CACHE_PATH' not in os.environ else os.environ['MEG_PLUGIN_CACHE_PATH']
