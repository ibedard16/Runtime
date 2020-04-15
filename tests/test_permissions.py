"""Runtime library unit testing for permissions"""

import os
import pytest
from meg_runtime import PermissionsManager


@pytest.fixture(scope='module')
def change_to_test_directory():
    cd = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    defaultPermFile = PermissionsManager.PERMISSION_FILE
    yield
    PermissionsManager.PERMISSION_FILE = defaultPermFile
    os.chdir(cd)


def test_permissions_00(change_to_test_directory):
    PermissionsManager.PERMISSION_FILE = 'test_permissions_00.json'
    PermissionsManager()


def test_permissions_01(change_to_test_directory):
    PermissionsManager.PERMISSION_FILE = 'test_permissions_01.json'
    perms = PermissionsManager()

    assert not perms.can_write('user2', 'a')


def test_permissions_02(change_to_test_directory):
    PermissionsManager.PERMISSION_FILE = 'test_permissions_01.json'
    perms = PermissionsManager()

    assert perms.can_write('user1', 'a')
    assert not perms.can_write('user1', 'b')
