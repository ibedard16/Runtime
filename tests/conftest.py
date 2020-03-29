"""Runtime tests configuration"""

import os
import sys

# Add the tests parent directory to be able to include runtime module
if isinstance(sys.path, list) and os.path.dirname(sys.path[0]) not in sys.path:
    sys.path.append(os.path.dirname(sys.path[0]))
