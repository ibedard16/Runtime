from PyQt5 import QtWidgets

from meg_runtime.plugins import PluginManager
from meg_runtime.ui.basepanel import BasePanel

class AddPluginPanel(BasePanel):
    """Setup the plugin panel."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_title(self):
        """Get the title of this panel."""
        return 'Add New Plugin'

    def on_load(self):
        """Load dynamic elements within the panel."""

        # Attach handlers
        instance = self.get_widgets()
        self.add_button = instance.findChild(QtWidgets.QPushButton, 'addButton')
        self.add_button.clicked.connect(self.add_plugin)
        self.available_plugin_list = instance.findChild(QtWidgets.QTreeWidget, 'availablePluginList')

        self.available_plugin_list.clear()

        # Add the file viewer/chooser
        available_plugins = PluginManager.get_all_available()
        for plugin in available_plugins:
            self.available_plugin_list.addTopLevelItem(QtWidgets.QTreeWidgetItem([
                plugin.name(),
                plugin.version(),
                plugin.author(),
                plugin.description()
            ]))
        
        self.available_plugin_list.addTopLevelItem(QtWidgets.QTreeWidgetItem([
                'test', '1.1.1', 'Isaac', 'A dynamic plugin that only exists to populate a list'
            ]))

    def add_plugin(self):
        """Open dialog to install a plugin"""
		# TODO
        pass