"""MEG system lockfile parser

Can be used to parse the lock file and perform operations on the lockfile
Only interacts with the lockfile, does not preform any git actions
Does not check permissions before actions are taken

All file paths are relitive to the repository directory
Working directory should be changed by the git module
"""

import json
import os.path
import time
from meg_runtime.logger import Logger
from collections.abc import MutableMapping


class LockFile(MutableMapping):
    """Parse a lockfile and preform locking operations
    """

    def __init__(self, filepath=None, blob=None):
        """Open a lockfile and initalize class with it
        Args:
            filepath (string): path to the lockfile
            blob (string): blob of json data
        """
        self._lockData = {}
        if blob is None:
            self.load(filepath)
        else:
            self.loads(blob)

    def __getitem__(self, filepath):
        """Get file entry, files have locks on them if and only if they have an entry
        Args:
            filepath (string): path of file that may be locked
        Returns:
            (dictionary): lockfile entry for the file
        """
        try:
            return self._lockData[filepath]
        except KeyError:
            return None

    def __setitem__(self, filepath, username):
        """Add or change a lock file entry
        Args:
            filepath (string): path of file to add lock to
            username (string): name of locking user
        """
        self._lockData[filepath] = {"user": username, "date": time.time()}

    def __delitem__(self, filepath):
        """Delete lockfile entry
        Args:
            filepath (string): path of file to add lock to
        """
        if filepath in self._lockData:
            del self._lockData[filepath]

    def __iter__(self):
        return iter(self._lockData)

    def __contains__(self, filepath):
        return filepath in self._lockData

    def __len__(self):
        return len(self._lockData)

    def save(self):
        """Saves current data into the lockfile, overriding its contents
        Must be ran to save any new or removed locks
        Will create file if it doesn't already exist
        """
        fileData = {
                    "comment": "MEG System locking file, do not manually editing",
                    "locks": self._lockData
                }
        json.dump(fileData, open(self._filepath, 'w'))

    def load(self, filepath=None):
        """Loads this object with the current data in the lockfile, overrideing its current data
        If the file doesn't exist, create one
        Args:
            filepath (string): path to the lockfile
        Returns:
            (bool): False if lockfile cannot be read
        """
        self._lockData = {}
        if(filepath is None):
            filepath = self._filepath
        else:
            self._filepath = filepath
            if(not os.path.exists(filepath)):
                self._createLockFile(filepath)
        try:
            self._lockData = json.load(open(filepath))["locks"]
        except (json.decoder.JSONDecodeError, KeyError):
            self._createLockFile(filepath)
            try:
                self._lockData = json.load(open(filepath))["locks"]
            except (json.decoder.JSONDecodeError, KeyError):
                Logger.warning("MEG Locking: Unable to read contents of lock file at {0}".format(self._filepath))
                return False
        return True

    def loads(self, s):
        """Loads this object with the current data in the lockfile, overrideing its current data
        If the file doesn't exist, create one
        Args:
            s (string | bytes | bytearray): a json containing string
        Returns:
            (bool): False if json was malformed
        """
        self._lockData = {}
        self._filepath = None
        try:
            self._lockData = json.loads(s)["locks"]
        except (json.decoder.JSONDecodeError, KeyError):
            Logger.warning("MEG Locking: Blob json is malformed")
            return False
        return True

    def _createLockFile(self, filepath):
        self._locks = {}
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.save()
