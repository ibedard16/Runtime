
import os.path
from PyQt5 import QtWidgets

from meg_runtime.app import App
from meg_runtime.config import Config
from meg_runtime.logger import Logger
from meg_runtime.ui.basepanel import BasePanel
from meg_runtime.ui.filechooser import FileChooser


class RepoPanel(BasePanel):
    """Setup the main file panel."""

    def __init__(self, repo_url=None, repo_path=None, repo=None, **kwargs):
        """RepoPanel constructor."""
        self._repo_url = repo_url
        self._repo_path = repo_path
        self._repo = repo
        super().__init__(**kwargs)
        self._branch_name_label.text = self.title

    def handle_double_clicked(self, item):
        """Handle double clicking of a file (open it with another program)."""
        # TODO
        path = self.tree_view.get_selected_path()

    @property
    def title(self):
        """Get the title for the panel."""
        return os.path.basename(self._repo_path) if self._repo_path else 'Project'

    def get_title(self):
        """Get the title of this panel."""
        return self.title

    def get_changes(self):
        """Do a pull for the repository."""
        if self._repo is not None:
            self._repo.pull()

    def send_changes(self):
        """Send changes for the given repo."""
        if self._repo is not None:
            self._repo.push()

    def on_load(self):
        """Load dynamic elements within the panel."""
        instance = self.get_widgets()
        self._main_button = instance.findChild(QtWidgets.QPushButton, 'mainMenu')
        self._main_button.clicked.connect(App.return_to_main)
        self._get_changes_button = instance.findChild(QtWidgets.QPushButton, 'getChanges')
        self._get_changes_button.clicked.connect(self.get_changes)
        self._send_changes_button = instance.findChild(QtWidgets.QPushButton, 'sendChanges')
        self._send_changes_button.clicked.connect(self.send_changes)
        self._branch_name_label = instance.findChild(QtWidgets.QLabel, 'branchName')
        # Setup the tree view of the repo if the repo folder exists
        path = Config.get('paths/user')
        if self._repo_path is not None:
            if os.path.exists(self._repo_path):
                path = self._repo_path
            else:
                Logger.warning(f'MEG RepoPanel: The path "{self._repo_path}" for this repo does not exist')
        self.tree_view = FileChooser(instance.findChild(QtWidgets.QTreeView, 'treeView'), path)
        # Setup a double click function if necessary
        self.tree_view.set_double_click_handler(self.handle_double_clicked)
