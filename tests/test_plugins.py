"""Runtime library unit testing for plugins"""

import os
import pytest
from meg_runtime import PluginManager


@pytest.fixture(scope='module')
def change_to_test_directory():
    cd = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    yield
    os.chdir(cd)


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


# Plugin remote archive install/uninstall test, this also tests install_archive by use and that tests install_path by use
def test_plugins_install_archive_from_url():
    """Plugin remote archive install/uninstall test, this also tests install_archive by use and that tests install_path by use"""
    assert PluginManager.install_archive_from_url('https://github.com/MultimediaExtensibleGit/Plugins/archive/master.zip')
    assert PluginManager.load('test')
    assert PluginManager.uninstall('test')
    assert PluginManager.install_archive_from_url('https://github.com/MultimediaExtensibleGit/Plugins/archive/master.tar.gz')
    assert PluginManager.load('test')
    assert PluginManager.uninstall('test')
