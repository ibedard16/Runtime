"""Runtime library unit testing for permissions"""

import os
import pytest
from meg_runtime.git.permissions import Permissions


@pytest.fixture(scope='module')
def change_to_test_directory():
    cd = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    defaultPermFile = Permissions.PERMISSION_PATH
    yield
    Permissions.PERMISSION_PATH = defaultPermFile
    os.chdir(cd)


def test_permissions_00(change_to_test_directory):
    Permissions.PERMISSION_PATH = 'test_permissions_00.json'
    Permissions(".")


def test_permissions_01(change_to_test_directory):
    Permissions.PERMISSION_PATH = 'test_permissions_01.json'
    perms = Permissions(".")

    assert not perms.can_write('user2', 'a')


def test_permissions_02(change_to_test_directory):
    Permissions.PERMISSION_PATH = 'test_permissions_01.json'
    perms = Permissions(".")

    assert perms.can_write('user1', 'a')
    assert not perms.can_write('user1', 'b')


def test_getUsers(change_to_test_directory):
    Permissions.PERMISSION_PATH = 'test_permissions_01.json'
    perms = Permissions(".")
    users = perms.get_users()
    for user, roles in users:
        if user == "user1":
            assert len(roles) == 2
            assert "manager" in roles
        if user == "user4":
            assert len(roles) == 3
            assert "manager" in roles
            assert "engineer" in roles


def test_grant_role(change_to_test_directory):
    Permissions.PERMISSION_PATH = 'test_permissions_01.json'
    perms = Permissions(".")
    perms.create_role("managerUser", "testRole")
    assert perms.grant_role("managerUser", "user2", "testRole")
    assert "testRole" in perms.get_roles_for_user("user2")
    assert not perms.grant_role("managerUser", "user2", "nonExistantRole")
    assert not perms.grant_role("engineerUser", "user3", "testRole")
    assert not perms.grant_role("engineerUser", "engineerUser", "manager")


def test_remove_role(change_to_test_directory):
    Permissions.PERMISSION_PATH = 'test_permissions_01.json'
    perms = Permissions(".")
    assert perms.remove_role("managerUser", "user2", "engineer")
    assert "engineer" not in perms.get_roles_for_user("user2")
    assert not perms.grant_role("engineerUser", "managerUser", "manager")


def test_create_role(change_to_test_directory):
    Permissions.PERMISSION_PATH = 'test_permissions_01.json'
    perms = Permissions(".")
    assert perms.create_role("managerUser", "newRole")
    perms.grant_role("managerUser", "user2", "newRole")
    assert "newRole" in perms.get_roles_for_user("user2")
    assert not perms.create_role("engineerUser", "badRole")
    assert not perms.create_role("managerUser", "default")


def test_delete_role(change_to_test_directory):
    Permissions.PERMISSION_PATH = 'test_permissions_01.json'
    perms = Permissions(".")
    assert perms.delete_role("managerUser", "engineer")
    assert "engineer" not in perms.get_roles_for_user("engineerUser")
    assert not perms.delete_role("managerUser", "fakeRole")
    assert not perms.delete_role("engineerUser", "manager")
    assert not perms.delete_role("managerUser", "default")


def test_add_role_permission(change_to_test_directory):
    Permissions.PERMISSION_PATH = 'test_permissions_01.json'
    perms = Permissions(".")
    assert perms.add_role_permission("managerUser", "engineer", "roles_write")
    assert perms.can_write("engineerUser", "misc.txt")
    assert not perms.add_role_permission("engineerUser", "engineer", "roles_write")
    assert not perms.add_role_permission("managerUser", "fakeRole", "roles_write")
    with pytest.raises(KeyError):
        perms.add_role_permission("managerUser", "manager", "fakePermission")


def test_add_role_permission_file(change_to_test_directory):
    Permissions.PERMISSION_PATH = 'test_permissions_01.json'
    perms = Permissions(".")
    perms.set_file_readonly("managerUser", "potato.obj", True)
    assert perms.add_role_permission("managerUser", "engineer", "roles_write", "potato.obj")
    assert perms.can_write("engineerUser", "potato.obj")
    assert not perms.can_write("managerUser", "potato.obj")


def test_remove_role_permission(change_to_test_directory):
    Permissions.PERMISSION_PATH = 'test_permissions_01.json'
    perms = Permissions(".")
    perms.add_role_permission("managerUser", "engineer", "roles_write")
    assert not perms.remove_role_permission("engineerUser", "engineer", "roles_write")
    assert perms.remove_role_permission("managerUser", "engineer", "roles_write")
    assert not perms.can_write("engineerUser", "anything.py")
    assert not perms.remove_role_permission("managerUser", "fakeRole", "roles_write")
    with pytest.raises(KeyError):
        perms.remove_role_permission("managerUser", "manager", "fakePermission")


def test_remove_role_permission_file(change_to_test_directory):
    Permissions.PERMISSION_PATH = 'test_permissions_01.json'
    perms = Permissions(".")
    perms.add_role_permission("managerUser", "engineer", "roles_write", "potato.obj")
    assert not perms.remove_role_permission("engineerUser", "engineer", "roles_write", "potato.obj")
    assert perms.remove_role_permission("managerUser", "engineer", "roles_write", "potato.obj")
    assert not perms.can_write("engineerUser", "potato.obj")


def test_add_user_permission(change_to_test_directory):
    Permissions.PERMISSION_PATH = 'test_permissions_01.json'
    perms = Permissions(".")
    assert not perms.can_write("engineerUser", "misc.txt")
    assert perms.add_user_permission("managerUser", "engineerUser", "users_write")
    assert perms.can_write("engineerUser", "misc.txt")
    assert not perms.add_user_permission("engineerUser", "engineerUser", "users_add_locks")
    with pytest.raises(KeyError):
        perms.add_user_permission("managerUser", "managerUser", "fakePermission")


def test_add_user_permission_file(change_to_test_directory):
    Permissions.PERMISSION_PATH = 'test_permissions_01.json'
    perms = Permissions(".")
    perms.set_file_readonly("managerUser", "potato.obj", True)
    assert perms.add_user_permission("managerUser", "engineerUser", "users_write", "potato.obj")
    assert perms.can_write("engineerUser", "potato.obj")
    assert not perms.can_write("user2", "potato.obj")
    assert not perms.can_write("managerUser", "potato.obj")


def test_remove_user_permission(change_to_test_directory):
    Permissions.PERMISSION_PATH = 'test_permissions_01.json'
    perms = Permissions(".")
    perms.add_user_permission("managerUser", "engineerUser", "users_write")
    assert not perms.remove_user_permission("engineerUser", "engineerUser", "users_write")
    assert perms.remove_user_permission("managerUser", "engineerUser", "users_write")
    assert not perms.can_write("engineerUser", "potato.obj")
    with pytest.raises(KeyError):
        perms.remove_user_permission("managerUser", "managerUser", "fakePermission")


def test_remove_user_permission_file(change_to_test_directory):
    Permissions.PERMISSION_PATH = 'test_permissions_01.json'
    perms = Permissions(".")
    perms.add_user_permission("managerUser", "engineerUser", "users_write", "potato.obj")
    assert not perms.remove_user_permission("engineerUser", "engineerUser", "users_write", "potato.obj")
    assert perms.remove_user_permission("managerUser", "engineerUser", "users_write", "potato.obj")
    assert not perms.can_write("engineerUser", "potato.obj")


def test_set_readonly(change_to_test_directory):
    Permissions.PERMISSION_PATH = 'test_permissions_01.json'
    perms = Permissions(".")
    assert perms.can_write("managerUser", "potato.obj")
    assert perms.set_file_readonly("managerUser", "potato.obj", True)
    assert not perms.can_write("managerUser", "potato.obj")
    assert perms.set_file_readonly("managerUser", "potato.obj", False)
    assert perms.can_write("managerUser", "potato.obj")
    assert not perms.set_file_readonly("engineerUser", "potato.obj", False)
