

class PanelException(Exception):
    """Panel exception class."""

    def __init__(self, message, **kwargs):
        """Panel exception class constructor"""
        super().__init__(message, **kwargs)
