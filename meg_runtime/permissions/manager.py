"""Multimedia Extensible Git (MEG) permissions manager

All users always have the default role. All permissions can be removed from the default role, but the role can never be removed.
"""

import json
import os
from meg_runtime.logger import Logger


class PermissionsManager(dict):
    """Permissions manager - one for each repository"""

    PERMISSION_FILE = ".meg/permissions.json"

    def __init__(self):
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
            self.update(json.load(open(PermissionsManager.PERMISSION_FILE)))
        except FileNotFoundError as e:
            # Log that loading the configuration failed
            Logger.warning('MEG Permission: {0}'.format(e))
            Logger.warning('MEG Permission: Could not load permissions file <' + PermissionsManager.PERMISSION_FILE + '>, using default permissions')

    def get_users(self):
        """Returns a list of all users and their roles
        TODO
        Returns:
            (list((username, list(roles)))): List of truples containing usernames and a list of their roles
        """
        pass

    def can_lock(self, user):
        """Return True if the current user can lock a specific path"""
        return self._general_check(user, 'roles_add_locks', 'users_add_locks')

    def can_write(self, user, path):
        """Return True if the current user can write to a specific path"""
        roles = self._get_roles(user)
        fileHasPermissions = path in self['files']
        for role in roles:
            if role in self['general']['roles_write']:
                return True
            if fileHasPermissions and role in self['files'][path]['roles_write']:
                return True
        if user in self['general']['users_write']:
            return True
        if fileHasPermissions and user in self['files'][path]['users_write']:
            return True
        return False

    def can_remove_lock(self, user):
        return self._general_check('roles_remove_locks', 'users_remove_locks')

    def can_grant_permissions(self, user):
        return self._general_check('roles_grant', 'users_grant')

    def grant_role(self, role):
        pass

    def remove_role(self, role):
        pass

    def create_role(self, role):
        pass

    def delete_role(self, role):
        pass

    def add_role_permission(self, role, key, file=None):
        """Add a permission to a role
        Defaults to general permission, if file is given, permission will only apply to that file
        TODO

        Args:
            role (string): role name
            key (string): permission name
            file (string, optional): file path of file to grant role permission to
        """
        pass

    def remove_role_permission(self, role, key, file=None):
        pass

    def add_user_permission(self, user, key, file=None):
        pass

    def remove_user_permission(self, user, key, file=None):
        pass

    def _general_check(self, user, roleKey, userKey):
        roles = self._get_roles(user)
        for role in roles:
            if role in self['general'][roleKey]:
                return True
        if user in self['general'][userKey]:
            return True
        return False

    def save(self):
        """Save currenly held permissions / roles to file"""
        if not os.path.exists(PermissionsManager.PERMISSION_FILE):
            os.makedirs(os.path.dirname(PermissionsManager.PERMISSION_FILE), exist_ok=True)
        json.dump(self, open(PermissionsManager.PERMISSION_FILE, 'w+'))

    def _get_roles(self, user):
        """Get a list of users from the configuration file."""
        roles = [role for role in self['roles']
                 if user in self['roles'][role]]
        roles.insert(0, "default")
        return roles
