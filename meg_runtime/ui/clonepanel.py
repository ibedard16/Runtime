
from PyQt5 import QtWidgets
from meg_runtime.app import App
from meg_runtime.config import Config
from meg_runtime.ui.basepanel import BasePanel
from meg_runtime.ui.filechooser import FileChooser


class ClonePanel(BasePanel):
    """Setup the cloning panel."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def clone(self):
        """Clone the repository."""
        repo_url = self.server_text_edit.toPlainText()
        username = self.username_text_edit.toPlainText()
        password = self.password_text_edit.toPlainText()
        path = self._tree_view.get_selected_path()
        repo_path = None
        if path is not None:
            repo_path = path
        # Pass control to the manager
        App.clone(username, password, repo_url, repo_path)

    def get_title(self):
        """Get the title of this panel."""
        return 'Clone'

    def on_load(self):
        """Load dynamic elements within the panel."""
        # Attach handlers
        instance = self.get_widgets()
        self.ok_button = instance.findChild(QtWidgets.QPushButton, 'okButton')
        self.ok_button.clicked.connect(self.clone)
        self.back_button = instance.findChild(QtWidgets.QPushButton, 'backButton')
        self.back_button.clicked.connect(App.return_to_main)
        self.server_text_edit = instance.findChild(QtWidgets.QTextEdit, 'server')
        self.username_text_edit = instance.findChild(QtWidgets.QTextEdit, 'username')
        self.password_text_edit = instance.findChild(QtWidgets.QTextEdit, 'password')
        # Add the file viewer/chooser
        self._tree_view = FileChooser(instance.findChild(QtWidgets.QTreeView, 'treeView'), Config.get('path/user'))
