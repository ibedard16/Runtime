"""Multimedia Extensible Git (MEG) permissions manager"""

import json
from kivy.logger import Logger


class PermissionsManager(dict):
    """Permissions manager - one for each repository"""

    def __init__(self, path, user):
        """Load the repository permission file"""
        self._user = user
        try:
            self.update(json.load(open(path)))
        except Exception as e:
            # Log that loading the configuration failed
            Logger.warning('MEG Permission: {0}'.format(e))
            Logger.warning('MEG Permission: Could not load permissions file <' + path + '>')

    def can_lock(self, path):
        """Return True if the current user can lock a specific path"""
        return PermissionsManager.can_read() and PermissionsManager.can_write()

    def can_read(self, path):
        """Return True if the current user can read a specific path"""
        if 'files' not in self or path not in self['files']:
            Logger.warning('MEG Permission: Path <' + path + '> does not exist in the permissions file.')
            return False
        roles = self._get_roles()
        for role in roles:
            if role in self['files'][path]['roles_read']:
                return True
        return self._user in self['files'][path]['users_read']

    def can_write(self, path):
        """Return True if the current user can write to a specific path"""
        if 'files' not in self or path not in self['files']:
            Logger.warning('MEG Permission: Path <' + path + '> does not exist in the permissions file.')
            return False
        roles = self._get_roles()
        for role in roles:
            if role in self['files'][path]['roles_write']:
                return True
        return self._user in self['files'][path]['users_write']

    def _get_roles(self):
        """Get a list of users from the configuration file."""
        return [role for role in self['roles']
                if self._user in self['roles'][role]]
