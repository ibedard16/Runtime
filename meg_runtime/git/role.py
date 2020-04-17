

class Role():
    """Wrapper class to make interfacing with Roles easier"""

    def __init__(self, name: str, permissions: list = []):
        """sets the name, grants every permission present in permissions, (all others false by default)"""
        self.name = name
        # init permissions to false
        self.can_add_lock = False
        self.can_remove_lock = False
        self.can_write = False
        self.can_grant_permissions = False
        self.can_add_role = False
        # process permissions
        for permissionName in permissions:
            self.give_permission(permissionName)
    
    def give_permission(self, permissionName):
        """used for building the Role class, takes the permission name and maps it to a permission property"""
        if permissionName == 'roles_remove_locks':
            self.can_remove_lock = True
        elif permissionName == 'roles_add_locks':
            self.can_add_lock = True
        elif permissionName == 'roles_write':
            self.can_write = True
        elif permissionName == 'roles_grant':
            self.can_grant_permissions = True
        elif permissionName == 'roles_modify_roles':
            self.can_modify_roles = True