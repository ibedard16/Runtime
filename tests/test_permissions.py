"""Runtime library unit testing for permissions"""

import os
import pytest
from meg_runtime.git.permissions import Permissions


@pytest.fixture(scope='module')
def change_to_test_directory():
    cd = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    defaultPermFile = Permissions.PERMISSION_FILE
    yield
    Permissions.PERMISSION_FILE = defaultPermFile
    os.chdir(cd)


def test_permissions_00(change_to_test_directory):
    Permissions.PERMISSION_FILE = 'test_permissions_00.json'
    Permissions()


def test_permissions_01(change_to_test_directory):
    Permissions.PERMISSION_FILE = 'test_permissions_01.json'
    perms = Permissions()

    assert not perms.can_write('user2', 'a')


def test_permissions_02(change_to_test_directory):
    Permissions.PERMISSION_FILE = 'test_permissions_01.json'
    perms = Permissions()

    assert perms.can_write('user1', 'a')
    assert not perms.can_write('user1', 'b')
