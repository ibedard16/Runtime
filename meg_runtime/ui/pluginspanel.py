
from PyQt5 import QtWidgets
from meg_runtime.app import App
from meg_runtime.config import Config
from meg_runtime.plugins.manager import PluginManager
from meg_runtime import ui


class PluginsPanel(ui.BasePanel):
    """Setup the plugin panel."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._add_plugin_panel = None

    def get_title(self):
        """Get the title of this panel."""
        return 'Plugins'

    def get_add_plugin_panel(self):
        """Get the add plugin panel to spawn for this panel."""
        if self._add_plugin_panel is None:
            self._add_plugin_panel = ui.AddPluginPanel(self)
        return self._add_plugin_panel

    def on_load(self):
        """Load dynamic elements within the panel."""
        instance = self.get_widgets()
        self.enable_button = instance.findChild(QtWidgets.QPushButton, 'enableButton')
        self.enable_button.clicked.connect(self.enableCurrentPlugin)
        self.disable_button = instance.findChild(QtWidgets.QPushButton, 'disableButton')
        self.disable_button.clicked.connect(self.disableCurrentPlugin)
        self.uninstall_button = instance.findChild(QtWidgets.QPushButton, 'uninstallButton')
        self.uninstall_button.clicked.connect(self.uninstallCurrentPlugin)
        self.add_button = instance.findChild(QtWidgets.QPushButton, 'addButton')
        self.add_button.clicked.connect(self.open_add_plugin)
        self.plugin_list = instance.findChild(QtWidgets.QTreeWidget, 'pluginList')
        self.plugin_list.itemSelectionChanged.connect(self.changeButtonStates)

    def on_show(self):
        """Showing the panel."""
        self.plugin_list.clear()
        for plugin in PluginManager.get_all():
            self.plugin_list.addTopLevelItem(QtWidgets.QTreeWidgetItem([
                chr(128309) if plugin.enabled() else chr(9898),
                plugin.name(),
                plugin.version(),
                plugin.author(),
                plugin.description()
            ]))
        # disable buttons
        self.changeButtonStates()

    def on_close(self):
        """Closing the panel."""
        # Hide the add plugins panel when the plugins panel is hidden
        App.get_window().remove_view(self.get_add_plugin_panel())

    def open_add_plugin(self):
        """"Open the new plugin window"""
        App.get_window().push_view(self.get_add_plugin_panel())

    def changeButtonStates(self):
        item = self.plugin_list.currentItem()
        plugin = None if item is None else PluginManager.get(item.text(1))
        if plugin is None:
            self.enable_button.setEnabled(False)
            self.disable_button.setEnabled(False)
            self.uninstall_button.setEnabled(False)
        else:
            self.enable_button.setEnabled(not plugin.enabled())
            self.disable_button.setEnabled(plugin.enabled())
            self.uninstall_button.setEnabled(True)

    def enableCurrentPlugin(self):
        item = self.plugin_list.currentItem()
        if item is not None and PluginManager.load_and_enable(item.text(1)):
            item.setText(0, chr(128309))
            Config.save()
            self.changeButtonStates()

    def disableCurrentPlugin(self):
        item = self.plugin_list.currentItem()
        if item is not None and PluginManager.disable(item.text(1)):
            item.setText(0, chr(9898))
            Config.save()
            self.changeButtonStates()

    def uninstallCurrentPlugin(self):
        item = self.plugin_list.currentItem()
        if item is not None and PluginManager.uninstall(item.text(1)):
            Config.save()
            (item.parent() or self.plugin_list.invisibleRootItem()).removeChild(item)
            self.changeButtonStates()
