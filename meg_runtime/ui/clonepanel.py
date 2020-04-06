
from PyQt5 import QtWidgets, uic
import pkg_resources

from meg_runtime.git import GitManager
from meg_runtime.config import Config
from meg_runtime.logger import Logger
from meg_runtime.ui.basepanel import BasePanel


class ClonePanel(BasePanel):
    """Setup the cloning panel.
    """
    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager

        self.ok_button = self.findChild(QtWidgets.QPushButton, 'okButton')
        self.ok_button.clicked.connect(self.clone)
        self.back_button = self.findChild(QtWidgets.QPushButton, 'backButton')
        self.back_button.clicked.connect(self.return_to_main_menu)

    def clone(self):
        """Clone the repository."""
        # Pass control to the manager
        self.manager.clone()

    def return_to_main_menu(self):
        """Return to the main menu."""
        self.manager.return_to_main_menu()


