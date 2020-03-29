"""Runtime library unit testing for configuration"""

import os
import sys
from meg_runtime import Config


# Configuration load/save test
def test_config_load_save():
    """Configuration load/save test"""
    # Load configuration to prevent removing anything already configured
    assert Config.load()
    # Set a test value and save the configuration
    assert Config.set('/test/key', 'value')
    assert Config.save()
    # Change the test value and reload the configuration
    assert Config.set('/test/key', 'alternate value')
    assert Config.load()
    # Check the test value is what was saved
    assert Config.get('test/key', 'default value') == 'value'
    # Remove the test value and resave the configuration
    assert Config.remove('test/key')
    assert Config.save()


# Configuration set/get test
def test_config_set_get():
    """Configuration set/get test"""
    assert Config.set('/test/key', 'value')
    assert Config.get('/test/key') == 'value'
    assert Config.set('test/key', '$(/test/key)value')
    assert Config.get('/test/key') == 'value'


# Configuration set/expand test
def test_config_set_expand():
    """Configuration set/expand test"""
    # Test set/expand
    assert Config.set('/test/key', 'value')
    assert Config.expand('$(/test/key)') == 'value'
    # Test nested expansion
    assert Config.set('test/key', '$(test/key)value')
    assert Config.expand('$(test/key)') == 'value'
    # Test multiple nested expansion
    assert Config.set('test/key1', '$(test/key3)value')
    assert Config.set('test/key2', '$(test/key1)value')
    assert Config.set('test/key3', '$(test/key2)value')
    assert Config.expand('$(test/key1)') == 'valuevaluevalue'
    assert Config.expand('$(test/key2)') == 'valuevaluevalue'
    assert Config.expand('$(test/key3)') == 'valuevaluevalue'


# Configuration set/exists test
def test_config_set_exists():
    """Configuration set/exists test"""
    assert Config.set('/test/key', 'value')
    assert Config.exists('/test/key')
    assert not Config.exists('/test/no/key')


# Configuration set/remove test
def test_config_set_remove():
    """Configuration set/remove test"""
    assert Config.set('test/key', 'value')
    assert Config.get('test/key', '') != ''
    assert Config.remove('test/key')
    assert Config.remove('test/no/key')
    assert Config.get('test/key', 'default') == 'default'


# Configuration invalid key test
def test_config_invalid_key():
    """Configuration invalid key test"""
    assert not Config.set('', 'value')
    assert Config.set('/test/key', 'value')
    assert not Config.set('/test/key/invalid', 'new value')
    assert not Config.set('/path/user', 'this can not be set!')
    assert not Config.set('path/config', 'this can not be set either...')
