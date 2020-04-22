import copy
import os.path
from PyQt5 import QtWidgets

from meg_runtime.app import App
from meg_runtime.git.role import Role
from meg_runtime import ui
from meg_runtime.ui.manager import UIManager
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
        self._all_roles = list(self._permissions.get_roles().values())
        for role in self._all_roles:
            self.role_list_widget.addTopLevelItem(QtWidgets.QTreeWidgetItem([
                role.name,
                self._get_permission_display_char(role.can_add_lock),
                self._get_permission_display_char(role.can_remove_lock),
                self._get_permission_display_char(role.can_write),
                self._get_permission_display_char(role.can_grant_permissions),
                self._get_permission_display_char(role.can_modify_roles),
            ]))

    def open_add_role(self):
        """Opens the panel to add a new role"""
        newRole = Role('new role')
        App.get_window().popup_view(ui.RoleEditPanel(self._permissions, newRole, True))

    def open_edit_role(self):
        """Opens the panel to edit a specific role"""
        currentRoleIndex = self._get_current_role_index()
        App.get_window().popup_view(ui.RoleEditPanel(self._permissions, self._all_roles[currentRoleIndex], False))

    def delete_role(self):
        """removes the role from the list"""
        currentRoleIndex = self._get_current_role_index()
        if currentRoleIndex is not None:
            currentRoleName = self._all_roles[currentRoleIndex].name
            if currentRoleName == 'default':
                QtWidgets.QMessageBox().critical(App.get_window(), App.get_name(), 'Cannot delete the default role, it is the role everyone has by default!')
                return
            self._permissions.delete_role('user', currentRoleName) #todo: use actual user name
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
        currentRoleIndex = self._get_current_role_index()
        self.edit_button.setEnabled(currentRoleIndex is not None)
        self.delete_button.setEnabled(currentRoleIndex is not None)

    def _get_current_role_index(self):
        """returns the currently selected role"""
        selectedRoleItem = self.role_list_widget.currentItem()
        if selectedRoleItem is None:
            return None
        selectedRoleIndex = self.role_list_widget.indexOfTopLevelItem(selectedRoleItem)
        return selectedRoleIndex

    def _get_permission_display_char(self, permission):
        if permission:
            return chr(10004) # check mark
        else:
            return ''
