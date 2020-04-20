
from PyQt5 import QtCore, QtWebEngineWidgets
from meg_runtime.ui.basepanel import BasePanel
from meg_runtime.app import App


class WebPanel(BasePanel):
    """Setup a list of cloned repos."""

    def __init__(self, url, **kwargs):
        """MainPanel constructor."""
        self._url = url
        super().__init__(**kwargs)

    def get_title(self):
        """Get the title of this panel."""
        title = '' if self._widgets is None else self._widgets.title()
        if not title:
            title = 'Loading...' if self._url is None else self._url
        return title

    def get_status(self):
        """Get the status of this panel."""
        return '' if self._url is None else self._url

    def get_icon(self):
        """Get the icon image of this panel."""
        icon = self._widgets.icon()
        return None if self._widgets is None else icon

    def on_load(self):
        """Load dynamic elements within the panel."""
        self._widgets = QtWebEngineWidgets.QWebEngineView()
        self._widgets.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self._widgets.load(QtCore.QUrl(self._url))
        self._widgets.iconChanged.connect(self._update_title)
        self._widgets.titleChanged.connect(self._update_title)

    def _update_title(self, title):
        App.get_window().set_title(self)
