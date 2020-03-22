"""Runtime library unit testing"""

import os
import sys

if isinstance(sys.path, list) and os.path.dirname(sys.path[0]) not in sys.path:
    sys.path.insert(1, os.path.dirname(sys.path[0]))

from meg_runtime import Config, GitManager, PermissionsManager, Plugin, PluginManager


# General runtime test
def test_runtime():
    """General runtime test"""
    pass
