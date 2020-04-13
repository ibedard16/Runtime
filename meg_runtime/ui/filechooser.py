
from PyQt5 import QtWidgets

import os


class FileChooser(object):
    """File chooser view (using composition)."""

    def __init__(self, tree_view, path, **kwargs):
        """File chooser constructor."""
        super().__init__(**kwargs)
        self._tree_view = tree_view
        model = QtWidgets.QDirModel()
        self._tree_view.setModel(model)
        self._tree_view.setRootIndex(model.index(path))

    def get_selected_path(self):
        """Return the selected path in the chooser."""
        indexes = self._tree_view.selectedIndexes()
        path = None
        if len(indexes) > 0:
            # Build up the selected path
            index = indexes[0]
            p = [index.data()]
            parent = index.parent()
            while parent.isValid():
                p.insert(0, parent.data())
                parent = parent.parent()
            path = '/'.join(p)
            # Handle Windows backslash
            if os.name == 'nt':
                path = '\\'.join(p)
        return path

    def set_double_click_handler(self, handler):
        """Set the double click handler."""
        self._tree_view.doubleClicked.connect(handler)
