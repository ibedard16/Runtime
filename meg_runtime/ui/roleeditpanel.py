from PyQt5 import QtWidgets

from meg_runtime.app import App
from meg_runtime.ui.basepanel import BasePanel

class RoleEditPanel(BasePanel):

    def __init__(self, rolesList, role, addNewRole, **kwargs):
        super().__init__(**kwargs)
        self._rolesList = rolesList
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
            self._rolesList.append(self._role)
        self._popup.accept()

    def cancel(self):
        self._popup.reject()