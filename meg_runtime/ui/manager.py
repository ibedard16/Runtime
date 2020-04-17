"""MEG UI Manager
"""

import pkg_resources
from PyQt5 import QtWidgets, QtGui, uic
from meg_runtime.logger import Logger
from meg_runtime.app import App


class UIManager(QtWidgets.QMainWindow):
    """Main UI manager for the MEG system."""

    UI_FILE = 'mainwindow.ui'

    # The window class widgets
    __widgets = None

    def __init__(self, **kwargs):
        """UI manager constructor."""
        # Load window resource if needed
        if UIManager.__widgets is None:
            # Load the resource setup from the package
            UIManager.__widgets = uic.loadUiType(pkg_resources.resource_filename(__name__, UIManager.UI_FILE))
        # Initialize the super class
        super().__init__(**kwargs)
        # Setup window resource
        UIManager.__widgets[0]().setupUi(self)
        # Set the window panel stack
        self._panels = None
        # Set handler for closing a panel
        self._panelwidget = self.findChild(QtWidgets.QTabWidget, 'panelwidget')
        self._panelwidget.tabCloseRequested.connect(self.remove_view_by_index)
        self._panelwidget.tabBarClicked.connect(self._show_view_by_index)
        # Set handlers for main buttons
        # TODO: Add more handlers for these
        self._action_clone = self.findChild(QtWidgets.QAction, 'action_Clone')
        self._action_clone.triggered.connect(App.open_clone_panel)
        self._action_open = self.findChild(QtWidgets.QAction, 'action_Open')
        self._action_open.triggered.connect(App.open_clone_panel)
        self._action_quit = self.findChild(QtWidgets.QAction, 'action_Quit')
        self._action_quit.triggered.connect(App.quit)
        self._action_about = self.findChild(QtWidgets.QAction, 'action_About')
        self._action_about.triggered.connect(App.open_about)
        self._action_manage_plugins = self.findChild(QtWidgets.QAction, 'action_Manage_Plugins')
        self._action_manage_plugins.triggered.connect(App.open_manage_plugins)
        # Set the default title
        self.set_title()
        # Set the icon
        icon_path = App.get_icon()
        if icon_path is not None:
            self.setWindowIcon(QtGui.QIcon(icon_path))

    def set_title(self, panel=None):
        """Update the window title from the current panel"""
        # Set the new window title, if provided by the panel
        if panel is not None and panel.get_title():
            self.setWindowTitle(f'{App.get_name()} - {panel.get_title()}')
        else:
            self.setWindowTitle(f'{App.get_name()}')

    def get_panel_container(self):
        """Get the panel container widget"""
        return self._panelwidget

    def get_panels(self):
        """Get all the panels in the window panel stack"""
        if not isinstance(self._panels, list):
            self._panels = []
        return self._panels

    def get_panel(self, name):
        """Get a panel in the window panel stack by name"""
        # Check panels by name
        for panel in self.get_panels():
            if panel.get_name() == name:
                # Return the panel
                return panel
        # Panel not found
        return None

    def get_panel_by_index(self, index):
        """Get a panel in the window panel stack by index"""
        # Get panels
        panels = self.get_panels()
        # Get the panel by index
        return None if index < 0 or index >= len(panels) else panels[index]

    def get_current_panel(self):
        """Get the current panel in the window stack"""
        panels = self.get_panels()
        # Get the window central widget
        container = self.get_panel_container()
        if container is not None:
            # Get the index of the current panel
            index = container.currentIndex()
            if index < len(panels) and index >= 0:
                # Return the panel at that index
                return panels[index]
        # Panel not found
        return None

    def push_view(self, panel):
        """Push a panel onto the stack being viewed."""
        # Hide the current panel
        current_panel = self.get_current_panel()
        if current_panel is not None:
            current_panel.on_hide()
        # Show the current panel
        panel.on_show()
        # Update the title for the panel
        self.set_title(panel)
        # Get the window central widget
        container = self.get_panel_container()
        if container is not None:
            # Add the panel to the view stack
            widgets = panel.get_widgets()
            widgets.setParent(container)
            title = panel.get_title()
            index = container.addTab(widgets, 'Home' if not title else title)
            # Remove the close button if not closable
            tabbar = container.tabBar()
            if not panel.get_is_closable():
                tabbar.tabButton(index, QtWidgets.QTabBar.RightSide).deleteLater()
                tabbar.setTabButton(index, QtWidgets.QTabBar.RightSide, None)
            # Add the panel icon
            tabbar.setTabIcon(index, panel.get_icon())
            # Set the panel to the view
            container.setCurrentIndex(index)
            # Add the panel to the panel stack
            self.get_panels().append(panel)

    def set_view(self, panel):
        """Set the panel to be viewed in the stack or push the panel onto the stack being viewed."""
        panels = self.get_panels()
        # Get the window central widget
        container = self.get_panel_container()
        if container is not None:
            index = None
            try:
                # Get the index of the panel
                index = panels.index(panel)
            except Exception:
                pass
            if index is not None:
                # Hide the current panel
                current_panel = self.get_current_panel()
                if current_panel is not None:
                    current_panel.on_hide()
                # Show the current panel
                panel.on_show()
                # Update the title for the panel
                self.set_title(panel)
                # Set the new panel
                container.setCurrentIndex(index)
                # Do not continue since the panel was found do not push
                return
        # Push the panel instead because it was not found
        self.push_view(panel)

    def remove_view(self, panel):
        """Remove a panel from the stack being viewed."""
        # Check if the panel is closable
        if panel.get_is_closable():
            Logger.debug(f'MEG UI: Removing panel "{panel.get_name()}"')
            # Check if current panel
            current_panel = self.get_current_panel()
            is_current_panel = panel == current_panel
            if is_current_panel:
                # Hide the current panel
                current_panel.on_hide()
                # Show the current panel
                panel.on_show()
            # Get the window central widget
            container = self.get_panel_container()
            if container:
                # Remove the panel from the view stack
                container.removeTab(self.get_panels().index(panel))
                panel.get_widgets().setParent(None)
                # Get the new current panel
                current_panel = self.get_current_panel()
                # Show the new panel if needed
                if is_current_panel and current_panel is not None:
                    current_panel.on_show()
                # Update the title for the panel
                self.set_title(current_panel)

    def remove_view_by_index(self, index):
        """Remove a panel from the stack being viewed."""
        # Get the panel by index
        Logger.debug(f'MEG UI: Removing panel by index ({index})')
        panel = self.get_panel_by_index(index)
        if panel is not None and panel.get_is_closable():
            # Remove the panel
            self.remove_view(panel)

    def _show_view_by_index(self, index):
        """Show the panel on click"""
        # Get the panel by index
        panel = self.get_panel_by_index(index)
        # Get the current panel
        current_panel = self.get_current_panel()
        # Check if the panel is not the current panel
        if current_panel != panel:
            # Hide the current panel
            if current_panel is not None:
                current_panel.on_hide()
            # Show the new panel
            if panel is not None:
                Logger.debug(f'MEG UI: Showing panel "{panel.get_name()}"')
                panel.on_show()
