
from PyQt5 import QtWidgets
from meg_runtime.app import App
from meg_runtime.config import Config
from meg_runtime.logger import Logger
from meg_runtime.git import GitManager
from meg_runtime.ui.basepanel import BasePanel
from meg_runtime.ui.repopanel import RepoPanel
from meg_runtime.ui.filechooser import FileChooser


class ClonePanel(BasePanel):
    """Setup the cloning panel."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def clone(self):
        """Clone the repository."""
        # Setup repository
        repo_url = self.server_text_edit.toPlainText()
        username = self.username_text_edit.toPlainText()
        password = self.password_text_edit.toPlainText()
        repo_path = self._tree_view.get_selected_path()
        # TODO: Handle username + password
        # Set the config
        repo = GitManager.clone(repo_url, repo_path)
        if repo is not None:
            repos = Config.get('repos', defaultValue=[])
            repos.append({'url': repo_url, 'path': repo_path})
            Config.set('repos', repos)
            Config.save()
            App.get_window().push_view(RepoPanel(repo))
        else:
            Logger.warning(f'MEG UIManager: Could not clone repo "{repo_url}"')
            QtWidgets.QMessageBox.warning(App.get_window(), App.get_name(), f'Could not clone the repo "{repo_url}"')

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
