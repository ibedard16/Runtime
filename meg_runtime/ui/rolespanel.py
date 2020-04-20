import os.path
from PyQt5 import QtWidgets

from meg_runtime.ui.manager import UIManager
from meg_runtime.ui.basepanel import BasePanel


class RolesPanel(BasePanel):
    def __init__(self, repo, **kwargs):
        super().__init__(**kwargs)
        self._repo = repo

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
        self.edit_button = instance.findChild(QtWidgets.QPushButton, 'editButton')
        self.edit_button.setEnabled(False)
        self.edit_button.clicked.connect(self.open_edit_role)
        self.save_button = instance.findChild(QtWidgets.QPushButton, 'saveButton')
        self.save_button.setEnabled(False)
        self.cancel_button = instance.findChild(QtWidgets.QPushButton, 'cancelButton')
        # roles list
        self.role_list_widget = instance.findChild(QtWidgets.QTreeWidget, 'roleList')
        self.role_list_widget.itemSelectionChanged.connect(self.on_role_selection)

    def load_roles(self):
        """loads the roles from the current repo"""
        self.role_list_widget.clear()
        self._all_roles = self._repo.permissions.get_roles()
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
        # TODO: Implement
        pass

    def open_edit_role(self):
        """Opens the panel to edit a specific role"""
        # TODO: Implement
        pass

    def on_role_selection(self):
        """Enables the edit button if a role was selected, otherwise disables it"""
        currentRole = self.get_current_role()
        self.edit_button.setEnabled(currentRole is not None)

    def get_current_role(self):
        """returns the currently selected role"""
        selectedRole = self.role_list_widget.currentItem()
        if selectedRole is None:
            return None
        selectedRoleName = selectedRole.text(0)
        return selectedRoleName

    def _get_permission_display_char(self, permission):
        if permission:
            return chr(10004) # check mark
        else:
            return chr(128473) # x mark