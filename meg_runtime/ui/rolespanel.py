import copy
import os.path
from PyQt5 import QtWidgets

from meg_runtime.app import App
from meg_runtime import ui
from meg_runtime.ui.basepanel import BasePanel


class RolesPanel(BasePanel):
    def __init__(self, repo, **kwargs):
        self._repo = repo
        self._permissions = copy.deepcopy(repo.permissions)
        super().__init__(**kwargs)

    def get_title(self):
        """Get the title of this panel."""
        return 'Manage Roles - ' + os.path.basename(os.path.abspath(self._repo.path))

    def on_load(self):
        """Load static elements within the panel"""
        self.attach_ui_elements()
        (username, password) = App.open_credential_dialog()
        if not self._permissions.can_modify_roles(username):
            QtWidgets.QMessageBox().critical(App.get_window(), App.get_name(), 'Cannot delete the default role, it is the role everyone has by default!')
            App.get_window().remove_view(self)
        self._user = username

    def on_show(self):
        """Load dynamic elements within the panel"""
        self.load_roles()

    def attach_ui_elements(self):
        """Initialize component by attaching handlers for form fields"""
        instance = self.get_widgets()
        # buttons
        self.add_new_button = instance.findChild(QtWidgets.QPushButton, 'addNewButton')
        self.add_new_button.clicked.connect(self.open_add_role)
        self.delete_button = instance.findChild(QtWidgets.QPushButton, 'deleteButton')
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_role)
        self.edit_button = instance.findChild(QtWidgets.QPushButton, 'editButton')
        self.edit_button.setEnabled(False)
        self.edit_button.clicked.connect(self.open_edit_role)
        self.save_button = instance.findChild(QtWidgets.QPushButton, 'saveButton')
        self.save_button.clicked.connect(self.save)
        self.cancel_button = instance.findChild(QtWidgets.QPushButton, 'cancelButton')
        self.cancel_button.clicked.connect(self.cancel)
        # roles list
        self.role_list_widget = instance.findChild(QtWidgets.QTreeWidget, 'roleList')
        self.role_list_widget.itemSelectionChanged.connect(self.on_role_selection)

    def load_roles(self):
        """loads the roles from the current repo"""
        self.role_list_widget.clear()
        self._all_roles = list(self._permissions['roles'].keys())
        for role in self._all_roles:
            self.role_list_widget.addTopLevelItem(QtWidgets.QTreeWidgetItem([
                role,
                self._does_role_have_permission_char(role, 'roles_add_locks'),
                self._does_role_have_permission_char(role, 'roles_remove_locks'),
                self._does_role_have_permission_char(role, 'roles_write'),
                self._does_role_have_permission_char(role, 'roles_grant'),
                self._does_role_have_permission_char(role, 'roles_modify_roles'),
            ]))

    def open_add_role(self):
        """Opens the panel to add a new role"""
        App.get_window().popup_view(ui.RoleEditPanel(self._user, self._permissions, 'new role', True))

    def open_edit_role(self):
        """Opens the panel to edit a specific role"""
        currentRole = self._get_current_role()
        App.get_window().popup_view(ui.RoleEditPanel(self._user, self._permissions, currentRole, False))

    def delete_role(self):
        """removes the role from the list"""
        currentRole = self._get_current_role()
        if currentRole == 'default':
            QtWidgets.QMessageBox().critical(App.get_window(), App.get_name(), 'Cannot delete the default role, it is the role everyone has by default!')
            return
        self._permissions.delete_role(self._user, currentRole)
        self.load_roles()
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)

    def save(self):
        self._permissions.save()
        self._repo.permissions.load()

    def cancel(self):
        """closes the panel"""
        App.get_window().remove_view(self)

    def on_role_selection(self):
        """Enables the edit button if a role was selected, otherwise disables it"""
        currentRole = self._get_current_role()
        self.edit_button.setEnabled(currentRole is not None)
        self.delete_button.setEnabled(currentRole is not None)

    def _get_current_role(self):
        """returns the currently selected role"""
        selectedRoleItem = self.role_list_widget.currentItem()
        if selectedRoleItem is None:
            return None
        selectedRoleIndex = self.role_list_widget.indexOfTopLevelItem(selectedRoleItem)
        return self._all_roles[selectedRoleIndex]

    def _does_role_have_permission_char(self, role, permission):
        # chr(10004) is a checkmark
        return chr(10004) if self._permissions.does_role_have_permission(role, permission) else ''
