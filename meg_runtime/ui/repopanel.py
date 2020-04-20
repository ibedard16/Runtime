
import os
import platform
import subprocess
from PyQt5 import QtWidgets
from meg_runtime.app import App
from meg_runtime.config import Config
from meg_runtime.logger import Logger
from meg_runtime.ui.basepanel import BasePanel
from meg_runtime.ui.filechooser import FileChooser


class RepoPanel(BasePanel):
    """Setup the main file panel."""

    def __init__(self, repo, **kwargs):
        """RepoPanel constructor."""
        self._repo = repo
        super().__init__(**kwargs)

    def get_title(self):
        """Get the title of this panel."""
        return f'{os.path.basename(os.path.abspath(self._repo.path))} : {self._repo.head.shorthand}'

    def get_status(self):
        """Get the status of this panel."""
        return f'{self._repo.head.shorthand} : {self._repo.path}'

    def get_changes(self):
        """Do a pull for the repository."""
        if self._repo is not None:
            self._repo.pull()

    def send_changes(self):
        """Send changes for the given repo."""
        if self._repo is not None:
            self._repo.push()
        
    def manage_roles(self):
        """Manage roles for the given repo"""
        if self._repo is not None:
            App.open_manage_roles(self._repo)

    def on_load(self):
        """Load dynamic elements within the panel."""
        instance = self.get_widgets()
        self._get_changes_button = instance.findChild(QtWidgets.QPushButton, 'getChanges')
        self._get_changes_button.clicked.connect(self.get_changes)
        self._send_changes_button = instance.findChild(QtWidgets.QPushButton, 'sendChanges')
        self._send_changes_button.clicked.connect(self.send_changes)
        self._manage_roles_button = instance.findChild(QtWidgets.QPushButton, 'manageRoles')
        self._manage_roles_button.clicked.connect(self.manage_roles)
        self._branch_name_label = instance.findChild(QtWidgets.QLabel, 'branchName')
        # Setup the tree view of the repo if the repo folder exists
        if os.path.exists(self._repo.path):
            path = self._repo.path
            self.tree_view = FileChooser(instance.findChild(QtWidgets.QTreeView, 'treeView'), path)
            header = self.tree_view._tree_view.header()
            header.resizeSection(0, header.sectionSize(0) * 3)
            # Setup a double click function if necessary
            self.tree_view.set_double_click_handler(self._handle_double_clicked)
        else:
            Logger.warning(f'MEG RepoPanel: The path "{self._repo.path}" for this repo does not exist')

    def on_show(self):
        """Showing the panel."""
        self._branch_name_label.setText(self.get_status())

    def _handle_double_clicked(self, item):
        """Handle double clicking of a file (open it with another program)."""
        path = self.tree_view.get_selected_path()
        if not os.path.isdir(path):
            try:
                if platform.system() == 'Darwin':
                    subprocess.run(['open', path])
                elif platform.system() == 'Windows':
                    os.startfile(path)
                else:
                    subprocess.run(['xdg-open', path])
            except Exception as e:
                Logger.warning(f'MEG RepoPanel: {e}')
                Logger.warning(f'MEG RepoPanel: Could not open the file {path}')
                QtWidgets.QMessageBox.warning(App.get_window(), App.get_name(), f'Could not open file "{path}"')
