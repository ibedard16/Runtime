"""Runtime library unit testing for permissions"""

import os
import sys
import pytest
from meg_runtime import PermissionsManager


@pytest.fixture(scope='module')
def change_to_test_directory():
    cd = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    yield
    os.chdir(cd)


def test_permissions_00(change_to_test_directory):
    perms = PermissionsManager('test_permissions_00.json', 'abc8')


def test_permissions_01(change_to_test_directory):
    perms = PermissionsManager('test_permissions_01.json', 'user2')

    assert perms.can_read('a')
    assert not perms.can_write('a')


def test_permissions_02(change_to_test_directory):
    perms = PermissionsManager('test_permissions_01.json', 'user1')

    assert perms.can_read('a')
    assert perms.can_write('a')
    assert not perms.can_read('b')
    assert not perms.can_write('b')
