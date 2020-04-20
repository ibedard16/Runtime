
from PyQt5 import QtCore, QtWidgets
from meg_runtime.ui.basepanel import BasePanel


class PreferencesPanel(BasePanel):
    """Preferences for configuration."""

    def __init__(self, **kwargs):
        """PreferencesPanel constructor."""
        super().__init__(**kwargs)

    def get_title(self):
        """Get the title of this panel."""
        return 'Preferences'

    def on_load(self):
        """Load dynamic elements within the panel."""
        pass
