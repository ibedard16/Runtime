
from PyQt5 import QtWidgets

from meg_runtime.config import Config
from meg_runtime.ui.basepanel import BasePanel
from meg_runtime.ui.filechooser import FileChooser
from meg_runtime.ui.helpers import PanelException


class PluginsPanel(BasePanel):
    """Setup the plugin panel."""

    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)

    def on_load():
        """Load dynamic elements within the panel."""

        # Attach handlers
        self.enable_button = self.findChild(QtWidgets.QPushButton, 'enableButton')
        #self.enable_button.clicked.connect()
        self.disable_button = self.findChild(QtWidgets.QPushButton, 'disableButton')
        #self.disable_button.clicked.connect()
        self.uninstall_button = self.findChild(QtWidgets.QPushButton, 'uninstallButton')
        #self.uninstall_button.clicked.connect()
        self.plugin_list = self.findChild(QtWidgets.QTreeWidget, 'pluginList')

        instance = PluginsPanel.get_instance()
        # Add the file viewer/chooser
        pluginManager = PluginManager.get_instance();
		plugins = pluginManager.get_all()
        pluginItems = [
            QtWidgets.QTreeWidgetItem([
                plugin.enabled() ? 🔵 : ⚪
            ])
            for plugin in plugins
        ]
        self.plugin_list.addTopLevelItem(pluginItems)

