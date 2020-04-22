
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
        # Directory to clone the repo into
        self.directory = None

    def clone(self):
        """Clone the repository."""
        # TODO: Need to update the Home panel with the new repo
        # Setup repository
        username = None
        password = None
        if self.enter_credentials_radio.isChecked():
            (username, password) = App.open_credential_dialog()
        elif self.use_stored_credentials_radio.isChecked():
            pass
            # TODO
        repo_url = self.server_text_edit.text()
        repo_path = self.directory
        # TODO: Handle username+password
        # Set the config
        repo = GitManager.clone(repo_url, repo_path)
        if repo is not None:
            self._save_repo_entry_in_config(repo_url, repo_path)
            App.get_window().push_view(RepoPanel(repo))
        else:
            Logger.warning(f'MEG UIManager: Could not clone repo "{repo_url}"')
            QtWidgets.QMessageBox.warning(App.get_window(), App.get_name(), f'Could not clone the repo "{repo_url}"')

    def _save_repo_entry_in_config(self, repo_url, repo_path):
        repos = Config.get('repos', defaultValue=[])
        duplicate_found = False
        for index, repo in enumerate(repos):
            if repo['path'] == repo_path:
                repos[index]['url'] = repo_url
                duplicate_found = True
                break
        if not duplicate_found:
            repos.append({'url': repo_url, 'path': repo_path})
        Config.set('repos', repos)
        Config.save()

    def _save_repo_entry_in_config(self, repo_url, repo_path):
        repos = Config.get('repos', defaultValue=[])
        duplicate_found  = False
        for index, repo in enumerate(repos):
            if repo['path'] == repo_path:
                repos[index]['url'] = repo_url
                duplicate_found = True
                break
        if not duplicate_found:
            repos.append({'url': repo_url, 'path': repo_path})
        Config.set('repos', repos)
        Config.save()

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
        # Radio Buttons
        self.no_credentials_radio = instance.findChild(QtWidgets.QRadioButton, 'noCredenitalsRadio')
        self.enter_credentials_radio = instance.findChild(QtWidgets.QRadioButton, 'enterCredentialsRadio')
        self.use_stored_credentials_radio = instance.findChild(QtWidgets.QRadioButton, 'useStoredCredentialsRadio')
        # Add the choose folder handler
        self.choose_folder_button = instance.findChild(QtWidgets.QPushButton, 'chooseFolderButton')
        self.choose_folder_button.clicked.connect(self.choose_folder)
        self.server_text_edit = instance.findChild(QtWidgets.QLineEdit, 'server')
        self.chosen_directory_label = instance.findChild(QtWidgets.QLabel, 'chosenDirectoryLabel')

    def choose_folder(self):
        """Open a dialog for choosing an empty folder or creating one."""
        # TODO: Don't allow files to be shown
        dialog = QtWidgets.QFileDialog()
        # Only allow directories
        dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
        if dialog.exec_():
            self.directory = dialog.selectedFiles()[0]
            self.chosen_directory_label.setText(self.directory)
