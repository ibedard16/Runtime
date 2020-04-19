from PyQt5 import QtWidgets

from meg_runtime.ui.manager import UIManager
from meg_runtime.ui.basepanel import BasePanel


class RolesPanel(BasePanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_title(self):
        """Get the title of this panel."""
        return 'Manage Roles'

    def on_load(self):
        """Load dynamic elements within the panel."""
        self.attach_handlers()

    def attach_handlers(self):
        """Initialize component by attaching handlers for form fields"""
        instance = self.get_widgets()
        # buttons
        self.add_new_button = instance.findChild(QtWidgets.QPushButton, 'addNewButton')
        self.add_new_button.clicked.connect(self.open_add_role)
        self.edit_button = instance.findChild(QtWidgets.QPushButton, 'editButton')
        self.edit_button.clicked.connect(self.open_edit_role)
        # roles list
        self.available_plugin_list = instance.findChild(QtWidgets.QTreeWidget, 'roleList')
    
    def open_add_role(self):
        """Opens the panel to add a new role"""
        # TODO: Implement
        pass
    
    def open_edit_role(self):
        """Opens the panel to edit a specific role"""
        # TODO: Implement
        pass
    

        