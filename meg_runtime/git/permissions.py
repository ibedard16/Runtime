"""Multimedia Extensible Git (MEG) permissions manager

All users always have the default role. All permissions can be removed from the default role, but the role can never be removed.
"""

import json
import os
from meg_runtime.logger import Logger

class Permissions(dict):
    """Permissions manager - one for each repository"""

    PERMISSION_PATH = ".meg/permissions.json"

    ROLE_PERMISSIONS = [
        "roles_remove_locks",
        "roles_add_locks",
        "roles_write",
        "roles_grant",
        "roles_modify_roles"
    ]

    USER_PERMISSIONS = [
        "users_remove_locks",
        "users_add_locks",
        "users_write",
        "users_grant",
        "users_modify_roles"
    ]

    def __init__(self, path):
        """Load the repository permission file"""
        self.__path = os.path.join(path, Permissions.PERMISSION_PATH)
        self.load()

    def get_users(self):
        """Returns a list of all users and their roles

        Returns:
            ([(user(string), [role(string)])]): List of truples containing usernames and a list of their roles
        """
        users = {}
        for role, userList in self['roles'].items():
            for user in userList:
                if user in users:
                    users[user].append(role)
                else:
                    users[user] = [role]
        for roles in users.values():
            roles.append("default")
        return [(user, users[user]) for user in users.keys()]

    def can_lock(self, user):
        """Return True if the current user can lock a specific path"""
        return self._general_check(user, 'roles_add_locks', 'users_add_locks')

    def can_write(self, user, path):
        """Return True if the current user can write to a specific path"""
        roles = self.get_roles(user)
        fileHasPermissions = path in self['files']
        # Read only file flag denies global write permissions, allows write for file specific write permissions
        readOnly = fileHasPermissions and self['files'][path]['read_only']
        for role in roles:
            if not readOnly and role in self['general']['roles_write']:
                return True
            if fileHasPermissions and role in self['files'][path]['roles_write']:
                return True
        if not readOnly and user in self['general']['users_write']:
            return True
        if fileHasPermissions and user in self['files'][path]['users_write']:
            return True
        return False

    def can_remove_lock(self, user):
        return self._general_check(user, 'roles_remove_locks', 'users_remove_locks')

    def can_grant_permissions(self, user):
        return self._general_check(user, 'roles_grant', 'users_grant')

    def can_modify_roles(self, user):
        return self._general_check(user, 'roles_modify_roles', 'users_modify_roles')

    def grant_role(self, user, targetUser, role):
        """If user is allowd to grant roles, grant role to targetUser
        """
        if self.can_grant_permissions(user):
            if role in self["roles"]:
                self["roles"][role].append(targetUser)
                return True
        return False

    def remove_role(self, user, targetUser, role):
        """If user is allowd to grant roles, remove role from targetUser
        """
        if self.can_grant_permissions(user):
            if role in self["roles"]:
                if targetUser in self["roles"][role]:
                    self["roles"][role].remove(targetUser)
                    return True
        return False

    def create_role(self, user, role):
        """If user is allowd to modify roles, create the role. Cannot create existing role
        """
        if self.can_modify_roles(user) and role not in self["roles"] and role != "default":
            self["roles"][role] = []
            return True
        return False

    def delete_role(self, user, role):
        """If user is allowd to modify roles, delete the role. Cannot delete default role
        """
        if self.can_modify_roles(user) and role in self["roles"] and role != "default":
            for permission in Permissions.ROLE_PERMISSIONS:
                if role in self["general"][permission]:
                    self["general"][permission].remove(role)
            for path in self["files"]:
                if role in self["files"][path]["roles_write"]:
                    self["files"][path]["roles_write"].remove(role)
            del self["roles"][role]
            return True
        return False

    def add_role_permission(self, user, role, key, path=None):
        """Add a permission to a role
        Defaults to general permissions, if file is given, permission will only apply to that file

        Args:
            user (string): name of current user
            role (string): role name
            key (string): permission name
            path (string, optional): file path of file to grant role permission to
        Returns:
            (bool): True if role no longer has permission. False if role doesn't exist or unable to remove permission
        """
        if self.can_modify_roles(user) and role in self["roles"]:
            if path is None:
                self["general"][key].append(role)
            else:
                if path not in self["files"]:
                    self._generate_file_entry(path)
                self["files"][path][key].append(role)
            return True
        return False

    def remove_role_permission(self, user, role, key, path=None):
        """Removes the permissions of a role
        See add_role_permission
        """
        if self.can_modify_roles(user) and role in self["roles"]:
            if path is None:
                if role in self["general"][key]:
                    self["general"][key].remove(role)
            else:
                if path in self["files"] and role in self["files"][path][key]:
                    self["files"][path][key].remove(role)
            return True
        return False

    def does_role_have_permission(self, role, permissionKey):
        return role in self['general'][permissionKey]

    def add_user_permission(self, user, targetUser, key, path=None):
        """Add a permission to a user
        Defaults to general permissions, if file is given, permission will only apply to that file

        Args:
            user (string): name of current user
            targetUser (string): name of user to add permission to
            key (string): permission name
            path (string, optional): file path of file to grant role permission to
        Returns:
            (bool): True if user no longer has permission. False if unable to remove permission
        """
        if self.can_grant_permissions(user):
            if path is None:
                self["general"][key].append(targetUser)
            else:
                if path not in self["files"]:
                    self._generate_file_entry(path)
                self["files"][path][key].append(targetUser)
            return True
        return False

    def remove_user_permission(self, user, targetUser, key, path=None):
        """Removes the permissions of a user
        See add_user_permission
        """
        if self.can_grant_permissions(user):
            if path is None:
                if targetUser in self["general"][key]:
                    self["general"][key].remove(targetUser)
            else:
                if path in self["files"] and targetUser in self["files"][path][key]:
                    self["files"][path][key].remove(targetUser)
            return True
        return False

    def set_file_readonly(self, user, path, readonly):
        """Sets or unsets a file as read only
        """
        if self.can_grant_permissions(user):
            if path not in self["files"]:
                self._generate_file_entry(path)
            self["files"][path]["read_only"] = readonly
            return True
        return False

    def _general_check(self, user, roleKey, userKey):
        roles = self.get_roles(user)
        for role in roles:
            if role in self['general'][roleKey]:
                return True
        if user in self['general'][userKey]:
            return True
        return False

    def _generate_file_entry(self, path):
        self["files"][path] = {
            "roles_write": [],
            "users_write": [],
            "read_only": False
        }

    def save(self):
        """Save currenly held permissions / roles to file"""
        if not os.path.exists(self.__path):
            os.makedirs(os.path.dirname(self.__path), exist_ok=True)
        json.dump(self, open(self.__path, 'w+'))

    def load(self):
        """Load the repository permission file"""
        self.update({
            "roles": {
                "default": [],
                "admin": []
            },
            "files": {},
            "general": {
                "users_remove_locks": [],
                "roles_remove_locks": ["default", "admin"],
                "users_add_locks": [],
                "roles_add_locks": ["default", "admin"],
                "users_write": [],
                "roles_write": ["default", "admin"],
                "users_grant": [],
                "roles_grant": ["default", "admin"],
                "users_modify_roles": [],
                "roles_modify_roles": ["default", "admin"]
            }
        })
        try:
            self.update(json.load(open(self.__path)))
        except FileNotFoundError:
            # Log that loading the configuration failed
            Logger.info('MEG PERMISSIONS: Could not load permissions file <' + self.__path + '>, using default permissions')

    def get_roles(self, user):
        """Get a list of roles applied to given user"""
        roles = [role for role in self['roles']
                 if user in self['roles'][role]]
        roles.insert(0, "default")
        return roles

    def rename_role(self, user, role, newRoleName):
        """Rename role, cannot rename default"""
        if self.can_modify_roles(user) and role in self["roles"] and newRoleName not in self["roles"] and role != "default" and newRoleName != "default":
            for permission in Permissions.ROLE_PERMISSIONS:
                if role in self["general"][permission]:
                    self["general"][permission].remove(role)
                    self["general"][permission].append(newRoleName)
            for path in self["files"]:
                if role in self["files"][path]["roles_write"]:
                    self["files"][path]["roles_write"].remove(role)
                    self["files"][path]["roles_write"].append(newRoleName)
            self["roles"][newRoleName] = self["roles"][role]
            del self["roles"][role]
            return True
        return False
