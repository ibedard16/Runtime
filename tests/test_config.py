"""Runtime library unit testing for configuration"""

import os
import sys

if isinstance(sys.path, list) and os.path.dirname(sys.path[0]) not in sys.path:
    sys.path.insert(1, os.path.dirname(sys.path[0]))

from meg_runtime import Config


# Configuration set/get test
def test_config_set_get():
    """Configuration set/get test"""
    Config.set('/path/to/key', 'value')
    assert Config.get('/path/to/key') == 'value'
    Config.set('key/path', '$(key/path)value')
    assert Config.get('key/path') == 'value'


# Configuration set/expand test
def test_config_set_expand():
    """Configuration set/expand test"""
    # Test set/expand
    Config.set('/path/to/key', 'value')
    assert Config.expand('$(/path/to/key)') == 'value'
    # Test nested expansion
    Config.set('key/path', '$(key/path)value')
    assert Config.expand('$(key/path)') == 'value'
    # Test multiple nested expansion
    Config.set('key/path1', '$(key/path3)value')
    Config.set('key/path2', '$(key/path1)value')
    Config.set('key/path3', '$(key/path2)value')
    assert Config.expand('$(key/path1)') == 'valuevaluevalue'
    assert Config.expand('$(key/path2)') == 'valuevaluevalue'
    assert Config.expand('$(key/path3)') == 'valuevaluevalue'


# Configuration set/exists test
def test_config_set_exists():
    """Configuration set/exists test"""
    Config.set('/path/to/key', 'value')
    assert Config.exists('/path/to/key')
    assert not Config.exists('/path/to/no/key')


# Configuration set/remove test
def test_config_set_remove():
    """Configuration set/remove test"""
    Config.set('key/path', 'value')
    assert Config.get('key/path', '') != ''
    Config.remove('key/path')
    assert Config.get('key/path', 'default') == 'default'
