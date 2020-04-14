
from PyQt5 import QtWidgets

from meg_runtime.ui.basepanel import BasePanel
from meg_runtime.logger import Logger


class PluginsPanel(BasePanel):
    """Setup the plugin panel."""

    def __init__(self, manager, **kwargs):
        super().__init__(**kwargs)

    def get_title():
        """Get the title of this panel."""
        return 'Plugins'

    def on_load():
        """Load dynamic elements within the panel."""

        # Attach handlers
        instance = self.get_widgets()
        self.enable_button = instance.findChild(QtWidgets.QPushButton, 'enableButton')
        #self.enable_button.clicked.connect()
        self.disable_button = instance.findChild(QtWidgets.QPushButton, 'disableButton')
        #self.disable_button.clicked.connect()
        self.uninstall_button = instance.findChild(QtWidgets.QPushButton, 'uninstallButton')
        #self.uninstall_button.clicked.connect()
        self.plugin_list = instance.findChild(QtWidgets.QTreeWidget, 'pluginList')

        # Add the file viewer/chooser
        pluginManager = PluginManager.get_instance();
        plugins = pluginManager.get_all()
        pluginItems = [
            QtWidgets.QTreeWidgetItem([
                '🔵' if plugin.enabled()  else '⚪' 
            ])
            for plugin in plugins
        ]
        self.plugin_list.addTopLevelItem(pluginItems)

