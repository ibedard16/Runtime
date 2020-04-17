
import os.path
from PyQt5 import QtWidgets

from meg_runtime.app import App
from meg_runtime.config import Config
from meg_runtime.logger import Logger
from meg_runtime.ui.basepanel import BasePanel
from meg_runtime.ui.filechooser import FileChooser


class RepoPanel(BasePanel):
    """Setup the main file panel."""

    def __init__(self, repo, repo_url=None, **kwargs):
        """RepoPanel constructor."""
        self._repo = repo
        self._repo_url = repo_url
        super().__init__(**kwargs)

    def get_title(self):
        """Get the title of this panel."""
        return os.path.basename(os.path.abspath(self._repo.path))

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
        if os.path.exists(self._repo.path):
            path = self._repo.path
            self.tree_view = FileChooser(instance.findChild(QtWidgets.QTreeView, 'treeView'), path)
            # Setup a double click function if necessary
            self.tree_view.set_double_click_handler(self._handle_double_clicked)
        else:
            Logger.warning(f'MEG RepoPanel: The path "{self._repo.path}" for this repo does not exist')

    def on_show(self):
        """Showing the panel."""
        self._branch_name_label.setText(self._repo.head.shorthand)

    def _handle_double_clicked(self, item):
        """Handle double clicking of a file (open it with another program)."""
        # TODO
        path = self.tree_view.get_selected_path()
