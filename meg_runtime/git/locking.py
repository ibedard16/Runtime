"""MEG system file locking

To be used to lock files, unlock files, override locks, and view locks
Will confirm user roles and preform required git operations

All file paths are relitive to the repository directory
Working directory should be changed by the git module
"""

from meg_runtime.git.lockFile import LockFile


class Locking:
    """Used to prefrom all locking operations
    To be used to lock files, unlock files, override locks, and view locks
    """
    LOCKFILE_PATH = ".meg/locks.json"

    def __init__(self, repo, blob=None):
        self._lockFile = LockFile(Locking.LOCKFILE_PATH, blob=blob)
        self._repo = repo

    def addLock(self, filepath, username):
        """Adds the lock
        Args:
            repo (GitRepository): currently open repository that the file belongs to
            filepath (string): path to the file to lock
            username (string): username of current user
        Returns:
            (bool): was lock successfully added
        """
        if not self._repo.permissions.can_lock(username):
            return False
        if filepath in self._lockFile:
            return False
        else:
            self._lockFile[filepath] = username
            return True

    def removeLock(self, filepath, username):
        """Sync the repo, remove a lock from a file, and sync again
        Args:
            repo (GitRepository): currently open repository that the file belongs to
            filepath (string): path to file to unlock
            username (string): username of current user
        Returns:
            (bool): is there still a lock (was the user permitted to remove the lock)
        """
        lock = self._lockFile[filepath]
        if(lock is None):
            return True
        elif(lock["user"] == username or self._repo.permissions.can_remove_lock(username)):
            del self._lockFile[filepath]
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
        return self._lockFile[filepath]

    def locks(self):
        """Get the LockFile object
        """
        return self._lockFile

    def save(self):
        """Save current locks to the local lockfile
        """
        self._lockFile.save()

