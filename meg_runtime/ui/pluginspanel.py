
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
        self.enable_button.clicked.connect(self.enableCurrentPlugin)
        self.disable_button = instance.findChild(QtWidgets.QPushButton, 'disableButton')
        self.disable_button.clicked.connect(self.disableCurrentPlugin)
        self.uninstall_button = instance.findChild(QtWidgets.QPushButton, 'uninstallButton')
        self.uninstall_button.clicked.connect(self.uninstallCurrentPlugin)
        self.add_button = instance.findChild(QtWidgets.QPushButton, 'addButton')
        self.add_button.clicked.connect(UIManager.open_add_plugin)

        self.plugin_list = instance.findChild(QtWidgets.QTreeWidget, 'pluginList')
        self.plugin_list.itemSelectionChanged.connect(self.changeButtonStates)

        self.refreshPluginList()

    def refreshPluginList(self):
        self.plugin_list.clear()
        plugins = PluginManager.get_all()
        for plugin in plugins:
            self.plugin_list.addTopLevelItem(QtWidgets.QTreeWidgetItem([
                chr(128309) if plugin.enabled() else chr(9898),
                plugin.name(),
                plugin.version(),
                plugin.author(),
                plugin.description()
            ]))
        
        # disable buttons
        self.changeButtonStates()

    def changeButtonStates(self):
        selectedPlugin = self.getCurrentPlugin()
        if (selectedPlugin is None):
            self.enable_button.setEnabled(False)
            self.disable_button.setEnabled(False)
            self.uninstall_button.setEnabled(False)
            return

        self.enable_button.setEnabled(not selectedPlugin.enabled())
        self.disable_button.setEnabled(selectedPlugin.enabled())
        self.uninstall_button.setEnabled(True)

    def enableCurrentPlugin(self):
        selectedPlugin = self.getCurrentPlugin()
        if (selectedPlugin is None):
            return
        
        PluginManager.enable(selectedPlugin.name())
        self.refreshPluginList()

    def disableCurrentPlugin(self):
        selectedPlugin = self.getCurrentPlugin()
        if (selectedPlugin is None):
            return
        
        PluginManager.disable(selectedPlugin.name())
        self.refreshPluginList()

    def uninstallCurrentPlugin(self):
        selectedPlugin = self.getCurrentPlugin()
        if (selectedPlugin is None):
            return
        
        PluginManager.uninstall(selectedPlugin.name())
        self.refreshPluginList()

    def getCurrentPlugin(self):
        selectedPluginItem = self.plugin_list.currentItem()
        if (selectedPluginItem is None):
            return None
        
        selectedPluginName = selectedPluginItem.text(1)
        return PluginManager.get(selectedPluginName)

    



