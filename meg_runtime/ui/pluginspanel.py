
from PyQt5 import QtWidgets

from meg_runtime.plugins import PluginManager
from meg_runtime.ui.basepanel import BasePanel
from meg_runtime.ui.manager import UIManager

class PluginsPanel(BasePanel):
    """Setup the plugin panel."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_title(self):
        """Get the title of this panel."""
        return 'Plugins'

    def on_load(self):
        """Load dynamic elements within the panel."""

        # Attach handlers
        instance = self.get_widgets()
        self.enable_button = instance.findChild(QtWidgets.QPushButton, 'enableButton')
        #self.enable_button.clicked.connect()
        self.disable_button = instance.findChild(QtWidgets.QPushButton, 'disableButton')
        #self.disable_button.clicked.connect()
        self.uninstall_button = instance.findChild(QtWidgets.QPushButton, 'uninstallButton')
        #self.uninstall_button.clicked.connect()
        self.add_button = instance.findChild(QtWidgets.QPushButton, 'addButton')
        self.add_button.clicked.connect(UIManager.open_add_plugin)
        self.plugin_list = instance.findChild(QtWidgets.QTreeWidget, 'pluginList')

        self.plugin_list.clear()

        # Add the file viewer/chooser
        plugins = PluginManager.get_all()
        for plugin in plugins:
            self.plugin_list.addTopLevelItem(QtWidgets.QTreeWidgetItem([
                '🔵' if plugin.enabled() else '⚪',
                plugin.name(),
                plugin.version(),
                plugin.author(),
                plugin.description()
            ]))
        
        self.plugin_list.addTopLevelItem(QtWidgets.QTreeWidgetItem([
                '🔵', 'test', '1.1.1', 'Isaac', 'A dynamic plugin that only exists to populate a list'
            ]))


