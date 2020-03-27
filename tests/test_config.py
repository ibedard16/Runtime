"""Runtime library unit testing for configuration"""

import os
import sys

if isinstance(sys.path, list) and os.path.dirname(sys.path[0]) not in sys.path:
    sys.path.insert(1, os.path.dirname(sys.path[0]))

from meg_runtime import Config


# Configuration set/get test
def test_config_set_get():
    """Configuration set/get test"""
    assert Config.set('/path/to/key', 'value')
    assert Config.get('/path/to/key') == 'value'
    assert Config.set('key/path', '$(key/path)value')
    assert Config.get('key/path') == 'value'


# Configuration set/expand test
def test_config_set_expand():
    """Configuration set/expand test"""
    # Test set/expand
    assert Config.set('/path/to/key', 'value')
    assert Config.expand('$(/path/to/key)') == 'value'
    # Test nested expansion
    assert Config.set('key/path', '$(key/path)value')
    assert Config.expand('$(key/path)') == 'value'
    # Test multiple nested expansion
    assert Config.set('key/path1', '$(key/path3)value')
    assert Config.set('key/path2', '$(key/path1)value')
    assert Config.set('key/path3', '$(key/path2)value')
    assert Config.expand('$(key/path1)') == 'valuevaluevalue'
    assert Config.expand('$(key/path2)') == 'valuevaluevalue'
    assert Config.expand('$(key/path3)') == 'valuevaluevalue'


# Configuration set/exists test
def test_config_set_exists():
    """Configuration set/exists test"""
    assert Config.set('/path/to/key', 'value')
    assert Config.exists('/path/to/key')
    assert not Config.exists('/path/to/no/key')


# Configuration set/remove test
def test_config_set_remove():
    """Configuration set/remove test"""
    assert Config.set('key/path', 'value')
    assert Config.get('key/path', '') != ''
    assert Config.remove('key/path')
    assert Config.remove('key/path/not/here')
    assert Config.get('key/path', 'default') == 'default'


# Configuration invalid key test
def test_config_invalid_key():
    """Configuration invalid key test"""
    assert not Config.set('', 'value')
    assert Config.set('/valid/key', 'value')
    assert not Config.set('/valid/key/invalid', 'new value')
    assert not Config.set('/path/user', 'this can not be set!')
    assert not Config.set('path/config', 'this can not be set either...')
