
from PyQt5 import QtWidgets
from meg_runtime.ui.basepanel import BasePanel
from meg_runtime.config import Config
from meg_runtime.app import App


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
        instance = self.get_widgets()
        self._prefs_selector = instance.findChild(QtWidgets.QTreeWidget, 'preferencesSelector')
        self._prefs_selector.currentItemChanged.connect(self._current_item_changed)
        self._prefs_stack = instance.findChild(QtWidgets.QStackedWidget, 'preferencesStack')
        self._prefs_editor = instance.findChild(QtWidgets.QPlainTextEdit, 'preferencesEditor')
        self._prefs_save = instance.findChild(QtWidgets.QPushButton, 'saveEditorPreferences')
        self._prefs_save.clicked.connect(self._save_prefs_clicked)

    def on_show(self):
        """Showing the panel."""
        self._prefs_editor.setPlainText(Config.dump())

    def _current_item_changed(self, current, previous):
        """Preference selector item changed"""
        self._prefs_stack.setCurrentIndex(int(current.text(1)))

    def _save_prefs_clicked(self):
        """Advanced preferences editor saved"""
        if not Config.replace(self._prefs_editor.toPlainText()) or not Config.save():
            QtWidgets.QMessageBox.critical(App.get_window(), App.get_name(), f'Could not save the configuration "{Config.get("path/config")}"!')
