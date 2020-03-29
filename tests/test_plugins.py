"""Runtime library unit testing for plugins"""

import os
import sys
from meg_runtime import PluginManager


# Plugins update cache test
def test_plugins_update_cache():
    """Plugins update cache test"""
    assert PluginManager.update_cache()


# Plugins install test
def test_plugins_install():
    """Plugins install test"""
    assert PluginManager.install('test')
    assert PluginManager.get('test') is not None


# Plugins update test
def test_plugins_update():
    """Plugins update test"""
    assert PluginManager.update()


# Plugins setup test
def test_plugins_setup():
    """Plugins setup test"""
    assert PluginManager.setup_all()


# Plugins enable test
def test_plugins_enable():
    """Plugins enable test"""
    assert PluginManager.enable_all()


# Plugins load enabled test
def test_plugins_load_enabled():
    """Plugins load enabled test"""
    assert PluginManager.load_enabled()


# Plugins disable test
def test_plugins_disable():
    """Plugins disable test"""
    assert PluginManager.disable_all()


# Plugins load all test
def test_plugins_load_all():
    """Plugins load all test"""
    assert PluginManager.load_all()


# Plugins install test
def test_plugins_uninstall():
    """Plugins uninstall test"""
    assert PluginManager.uninstall('test')
    assert PluginManager.get('test') is None
