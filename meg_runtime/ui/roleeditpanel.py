from PyQt5 import QtWidgets

from meg_runtime.app import App
from meg_runtime.ui.basepanel import BasePanel


class RoleEditPanel(BasePanel):

    def __init__(self, user, permissions, role, addNewRole, **kwargs):
        super().__init__(**kwargs)
        self._user = user
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
        self._role_name_edit.setText(self._role)
        self._role_name_edit.setEnabled(self._role != 'default')  # cannot change the name of the default role
        self._add_locks_box.setChecked(self._permissions.does_role_have_permission(self._role, 'roles_add_locks'))
        self._remove_locks_box.setChecked(self._permissions.does_role_have_permission(self._role, 'roles_remove_locks'))
        self._modify_files_box.setChecked(self._permissions.does_role_have_permission(self._role, 'roles_write'))
        self._grant_permissions_box.setChecked(self._permissions.does_role_have_permission(self._role, 'roles_grant'))
        self._modify_roles_box.setChecked(self._permissions.does_role_have_permission(self._role, 'roles_modify_roles'))

    def cancel(self):
        self._popup.reject()

    def apply(self):
        errorMessage = None
        if self._addNewRole:
            errorMessage = self._add_new_role()
        else:
            errorMessage = self._edit_existing_role()
        if errorMessage is None:
            self._popup.accept()
        else:
            QtWidgets.QMessageBox().critical(App.get_window(), App.get_name(), errorMessage)

    def _add_new_role(self):
        self._role = self._role_name_edit.text()
        self._permissions.create_role(self._user, self._role)
        if self._add_locks_box.isChecked():
            self._permissions.add_role_permission(self._user, self._role, 'roles_add_locks')
        if self._remove_locks_box.isChecked():
            self._permissions.add_role_permission(self._user, self._role, 'roles_remove_locks')
        if self._modify_files_box.isChecked():
            self._permissions.add_role_permission(self._user, self._role, 'roles_write')
        if self._grant_permissions_box.isChecked():
            self._permissions.add_role_permission(self._user, self._role, 'roles_grant')
        if self._modify_roles_box.isChecked():
            self._permissions.add_role_permission(self._user, self._role, 'roles_modify_roles')

    def _edit_existing_role(self):
        editedRoleName = self._role_name_edit.text()
        if self._role != editedRoleName:
            renameSucceeded = self._permissions.rename_role(self._user, self._role, editedRoleName)
            if renameSucceeded:
                self._role = editedRoleName
            else:
                return f'Cannot rename role, a role with name: "{self._role}" already exists'
        self._toggle_role_permission_if_changed('roles_add_locks', self._add_locks_box.isChecked())
        self._toggle_role_permission_if_changed('roles_remove_locks', self._remove_locks_box.isChecked())
        self._toggle_role_permission_if_changed('roles_write', self._modify_files_box.isChecked())
        self._toggle_role_permission_if_changed('roles_grant', self._grant_permissions_box.isChecked())
        self._toggle_role_permission_if_changed('roles_modify_roles', self._modify_roles_box.isChecked())

    def _toggle_role_permission_if_changed(self, permissionName, newHasPermission):
        oldHasPermission = self._permissions.does_role_have_permission(self._role, permissionName)
        if oldHasPermission != newHasPermission:
            if newHasPermission:
                self._permissions.add_role_permission(self._user, self._role, permissionName)
            else:
                self._permissions.remove_role_permission(self._user, self._role, permissionName)
