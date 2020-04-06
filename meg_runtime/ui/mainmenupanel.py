
from PyQt5 import QtWidgets, uic
import pkg_resources

from meg_runtime.config import Config
from meg_runtime.logger import Logger
from meg_runtime.ui.basepanel import BasePanel


class MainMenuPanel(BasePanel):
    """Setup a list of cloned repos.
    """
    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager

        self.download_button = self.findChild(QtWidgets.QPushButton,
                                              'downloadButton')
        # TODO: Attach handlers
        self.download_button.clicked.connect(self.download)

    def download(self):
        """"Download" or clone a project."""
        # Pass control to the manager
        self.manager.open_clone_panel()



