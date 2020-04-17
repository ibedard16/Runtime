
import os.path
from PyQt5 import QtWidgets
from meg_runtime.app import App
from meg_runtime.config import Config
from meg_runtime.logger import Logger
from meg_runtime.ui.basepanel import BasePanel
from meg_runtime.ui.repopanel import RepoPanel
from meg_runtime.git.manager import GitManager


class MainPanel(BasePanel):
    """Setup a list of cloned repos."""

    def __init__(self, **kwargs):
        """MainPanel constructor."""
        super().__init__(App.get_icon(), **kwargs)

    def get_is_closable(self):
        """Get if the panel is closable."""
        return False

    def on_load(self):
        """Load dynamic elements within the panel."""
        instance = self.get_widgets()
        self.download_button = instance.findChild(QtWidgets.QPushButton, 'downloadButton')
        # TODO: Attach handlers
        self.download_button.clicked.connect(App.open_clone_panel)
        self._tree_widget = instance.findChild(QtWidgets.QTreeWidget, 'treeWidget')
        self._tree_widget.itemDoubleClicked.connect(self._handle_double_click)
        # Load the repos
        # TODO: Get this from the GitManager
        repos = Config.get('path/repos')
        repos = [
            QtWidgets.QTreeWidgetItem([
                os.path.basename(repo['path']),
                repo['path'],
                repo['url'],
            ])
            for repo in repos if repo['path'] and repo['url']
        ]
        self._tree_widget.clear()
        self._tree_widget.addTopLevelItems(repos)

    def _handle_double_click(self, item):
        """Handle a double click."""
        repo_path = 'unknown'
        try:
            repo_path = item.text(1)
            repo_url = item.text(2)
            # Open or clone the repo
            repo = GitManager.open_or_clone(repo_path, repo_url)
            # Create the repository panel
            App.get_window().push_view(RepoPanel(repo, repo_url))
        except Exception as e:
            Logger.warning(f'MEG UIManager: {e}')
            Logger.warning(f'MEG UIManager: Could not load repository "{repo_path}"')
            # Popup
            QtWidgets.QMessageBox.warning(App.get_window(), App.get_name(), f'Could not load repository "{repo_path}"')
