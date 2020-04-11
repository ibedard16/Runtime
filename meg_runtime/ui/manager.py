"""MEG UI Manager
"""
from PyQt5 import QtWidgets

from meg_runtime.ui.mainmenupanel import MainMenuPanel
from meg_runtime.ui.clonepanel import ClonePanel
from meg_runtime.ui.repopanel import RepoPanel


class UIManager(QtWidgets.QStackedWidget):
    """Main UI manager for the MEG system."""

    PANELS = [
        ClonePanel,
        MainMenuPanel,
        RepoPanel,
    ]

    def __init__(self, **kwargs):
        """UI manager constructor."""
        super().__init__(**kwargs)
        for panel in self.PANELS:
            self.addWidget(panel(self))
        self.change_view(MainMenuPanel)

    def open_clone_panel(self):
        """"Download" or clone a project."""
        # TODO
        self.change_view(ClonePanel)

    def clone(self):
        """Clone a repository."""
        # TODO
        self.change_view(RepoPanel)

    def return_to_main_menu(self):
        """Return to the main menu screen"""
        self.change_view(MainMenuPanel)

    def change_view(self, panel):
        """Change the current panel being viewed. """
        self.setCurrentIndex(self.PANELS.index(panel))

    # TODO: Add more menu opening/closing methods here
