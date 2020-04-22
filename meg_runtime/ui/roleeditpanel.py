from PyQt5 import QtWidgets

from meg_runtime.app import App
from meg_runtime.ui.basepanel import BasePanel

class RoleEditPanel(BasePanel):

    def __init__(self, permissions, role, addNewRole, **kwargs):
        super().__init__(**kwargs)
        self._permissions = permissions
        self._role = role
        self._addNewRole = addNewRole
    
    def on_load(self):
        instance = self.get_widgets()
        self._role_name_edit = instance.findChild(QtWidgets.QLineEdit, 'roleNameEdit')
        self._add_locks_box = instance.findChild(QtWidgets.QCheckBox, 'addLocksBox')
        self._remove_locks_box = instance.findChild(QtWidgets.QCheckBox, 'removeLocksBox')
        self._modify_files_box = instance.findChild(QtWidgets.QCheckBox, 'modifyFilesBox')
        self._grant_permissions_box = instance.findChild(QtWidgets.QCheckBox, 'grantPermissionsBox')
        self._modify_roles_box = instance.findChild(QtWidgets.QCheckBox, 'modifyRolesBox')
        # buttons
        self._applyButton = instance.findChild(QtWidgets.QPushButton, 'applyButton')
        self._applyButton.clicked.connect(self.apply)
        self._cancelButton = instance.findChild(QtWidgets.QPushButton, 'cancelButton')
        self._cancelButton.clicked.connect(self.cancel)
    
    def on_show(self):
        self._popup = App.get_window().get_current_popup()
        self._role_name_edit.setText(self._role.name)
        self._role_name_edit.setEnabled(self._addNewRole)
        self._add_locks_box.setChecked(self._role.can_add_lock)
        self._remove_locks_box.setChecked(self._role.can_remove_lock)
        self._modify_files_box.setChecked(self._role.can_write)
        self._grant_permissions_box.setChecked(self._role.can_grant_permissions)
        self._modify_roles_box.setChecked(self._role.can_modify_roles)

    def apply(self):
        self._role.name = self._role_name_edit.text()
        self._role.can_add_lock = self._add_locks_box.isChecked()
        self._role.can_remove_lock = self._remove_locks_box.isChecked()
        self._role.can_write = self._modify_files_box.isChecked()
        self._role.can_grant_permissions = self._grant_permissions_box.isChecked()
        self._role.can_modify_roles = self._modify_roles_box.isChecked()
        if self._addNewRole:
            self._permissions.create_role('user', self._role.name) # TODO: Use actual name
        self.apply_roles()
        self._popup.accept()

    def apply_roles(self):
        # TODO: Use actual user name
        # can add lock
        if self._role.can_add_lock:
            self._permissions.add_role_permission('user', self._role.name, 'roles_add_locks')
        else:
            self._permissions.remove_role_permission('user', self._role.name, 'roles_add_locks')
        # can remove lock
        if self._role.can_remove_lock:
            self._permissions.add_role_permission('user', self._role.name, 'roles_remove_locks')
        else:
            self._permissions.remove_role_permission('user', self._role.name, 'roles_remove_locks')
        # can write
        if self._role.can_write:
            self._permissions.add_role_permission('user', self._role.name, 'roles_write')
        else:
            self._permissions.remove_role_permission('user', self._role.name, 'roles_write')
        # can grant permission
        if self._role.can_grant_permissions:
            self._permissions.add_role_permission('user', self._role.name, 'roles_grant')
        else:
            self._permissions.remove_role_permission('user', self._role.name, 'roles_grant')
        # can modify roles
        if self._role.can_modify_roles:
            self._permissions.add_role_permission('user', self._role.name, 'roles_modify_roles')
        else:
            self._permissions.remove_role_permission('user', self._role.name, 'roles_modify_roles')

    def cancel(self):
        self._popup.reject()