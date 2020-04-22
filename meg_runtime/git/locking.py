"""MEG system file locking

To be used to lock files, unlock files, override locks, and view locks
Will confirm user roles and preform required git operations

All file paths are relitive to the repository directory
Working directory should be changed by the git module
"""

import time
import os
import json
from meg_runtime.logger import Logger


class Locking:
    """Used to prefrom all locking operations
    To be used to lock files, unlock files, override locks, and view locks
    """
    LOCKFILE_PATH = ".meg/locks.json"

    def __init__(self, permissions, path, blob=None):
        self.__permissions = permissions
        self.__lockData = {}
        self.__path = os.path.join(path, Locking.LOCKFILE_PATH)
        if blob is None:
            self.load()
        else:
            self.loads(blob)

    def addLock(self, username, filepath):
        """Adds the lock
        Args:
            username (string): username of current user
            filepath (string): path to the file to lock
        Returns:
            (bool): was lock successfully added
        """
        if not self.__permissions.can_lock(username):
            return False
        if filepath in self.__lockData:
            return False
        else:
            self.__lockData[filepath] = {"user": username, "date": time.time()}
            return True

    def removeLock(self, username, filepath):
        """Sync the repo, remove a lock from a file, and sync again
        Args:
            username (string): username of current user
            filepath (string): path to file to unlock
        Returns:
            (bool): is there still a lock (was the user permitted to remove the lock)
        """
        lock = self.findLock(filepath)
        if(lock is None):
            return True
        elif(lock["user"] == username or self.__permissions.can_remove_lock(username)):
            del self.__lockData[filepath]
        else:
            return False
        return True

    def findLock(self, filepath):
        """Find if there is a lock on the file, does not automatily sync the lock file
        Args:
            filepath (string): path of file to look for
        Returns:
            (dictionary): lockfile entry for the file
            (None): There is no entry
        """
        return self.__lockData.get(filepath, None)

    def findLocksByUser(self, username):
        """Find all locks owned by given user

        Args:
            username (string): git username of user
        Returns:
            [path(string)]: list of paths locked by user
        """
        locks = []
        for key, value in self.__lockData.items():
            if value["user"] == username:
                locks.append(key)
        return locks

    def removeLocksByUser(self, username):
        """Removes all locks owned by given user

        Args:
            username (string): git username of user
        """
        keysToRemove = []
        for key, value in self.__lockData.items():
            if value["user"] == username:
                keysToRemove.append(key)
        for key in keysToRemove:
            del self.__lockData[key]

    def addLocks(self, username, locks):
        """Creates locks for the given user
            If it fails, none of the locks will be added
            And if sucessful, all locks are added

        Args:
            username (string): git username of user
            locks ([path(string)]): list of paths of files to lock
        Returns:
            (bool): was sucessful
        """
        if not self.__permissions.can_lock(username):
            return False
        for lock in locks:
            if lock in self.__lockData:
                return False
        for lock in locks:
            self.__lockData[lock] = {"user": username, "date": time.time()}
        return True

    def clear(self):
        self.__lockData = {}

    @property
    def locks(self):
        """Get the dictionary of locks
        """
        return self.__lockData

    def save(self):
        """Saves current data into the lockfile, overriding its contents
        Must be ran to save any new or removed locks
        Will create file if it doesn't already exist
        """
        os.makedirs(os.path.dirname(self.__path), exist_ok=True)
        with open(self.__path, 'w+') as lockfile:
            json.dump(self.__lockData, lockfile)
            lockfile.close()

    def __iter__(self):
        return iter(self.__lockData)

    def __contains__(self, filepath):
        return filepath in self.__lockData

    def __len__(self):
        return len(self.__lockData)

    def load(self):
        """Loads this object with the current data in the locks file
        Discards the any currently held locks

        Args:
            filepath (string): path to the lockfile
        Returns:
            (bool): False if lockfile cannot be read
        """
        self.__lockData = {}
        self._generateLockFile()
        data = None
        try:
            with open(self.__path, 'r') as lockfile:
                data = json.load(lockfile)
                lockfile.close()
        except json.decoder.JSONDecodeError:
            Logger.warning("MEG Locking: Unable to read contents of lock file at {0}".format(self.__path))
            return False
        if data is not None:
            self.__lockData = data
        return True

    def loads(self, s):
        """Loads this object with the current data in the lockfile
        Discards the any currently held locks

        Args:
            s (string | bytes | bytearray): a json containing string
        Returns:
            (bool): False if json was malformed
        """
        self.__lockData = {}
        try:
            self.__lockData = json.loads(s)
        except json.decoder.JSONDecodeError:
            Logger.warning("MEG Locking: Blob json is malformed")
            return False
        return True

    def _generateLockFile(self):
        """If the lock file doesn't exist, generate the directory tree and create the file
        """
        if not os.path.isfile(self.__path):
            Logger.info("MEG LOCKING: GENERATING LOCK FILE")
            os.makedirs(os.path.dirname(self.__path), exist_ok=True)
            open(self.__path, 'w+').close()
