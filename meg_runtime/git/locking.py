"""MEG system file locking

To be used to lock files, unlock files, override locks, and view locks
Will confirm user roles and preform required git operations

All file paths are relitive to the repository directory
Working directory should be changed by the git module
"""

from meg_runtime.git.lockFile import LockFile
from meg_runtime.logger import Logger


class Locking:
    """Used to prefrom all locking operations
    To be used to lock files, unlock files, override locks, and view locks
    """
    LOCKFILE_PATH = ".meg/locks.json"

    def __init__(self):
        Locking._lockFile = LockFile(Locking.LOCKFILE_PATH)

    def addLock(self, repo, filepath, username):
        """Sync the repo, adds the lock, sync the repo
        Args:
            repo (GitRepository): currently open repository that the file belongs to
            filepath (string): path to the file to lock
            username (string): username of current user
        Returns:
            (bool): was lock successfully added
        """
        if not repo.permissions.can_lock(username):
            return False
        self.pullLocks(repo)
        if filepath in self._lockFile:
            return False
        else:
            self._lockFile[filepath] = username
            self.pushLocks(repo)
            return True

    def removeLock(self, repo, filepath, username):
        """Sync the repo, remove a lock from a file, and sync again
        Args:
            repo (GitRepository): currently open repository that the file belongs to
            filepath (string): path to file to unlock
            username (string): username of current user
        Returns:
            (bool): is there still a lock (was the user permitted to remove the lock)
        """
        self.pullLocks(repo)
        lock = self._lockFile[filepath]
        if(lock is None):
            return True
        elif(lock["user"] == username or repo.permissions.can_remove_lock(username)):
            del self._lockFile[filepath]
        else:
            return False
        self.pushLocks(repo)
        return True

    def findLock(self, filepath):
        """Find if there is a lock on the file, does not automatily sync the lock file
        Args:
            filepath (string): path of file to look for
        Returns:
            (dictionary): lockfile entry for the file
            (None): There is no entry
        """
        self._lockFile.load()
        return self._lockFile[filepath]

    def locks(self):
        """Get the LockFile object
        """
        self._lockFile.load()
        return self._lockFile

    def pullLocks(self, repo):
        """Pulls the lock file from remote and loads it

        Args:
            repo(GitRepository): currently open repository that the file belongs to
        """
        if repo is None:
            Logger.warning("MEG Locking: Could not open repositiory")
            return False
        # Fetch current version
        if not repo.pullPaths([Locking.LOCKFILE_PATH]):
            Logger.warning("MEG Locking: Could not download newest lockfile")

        self._lockFile.load()

    def pushLocks(self, repo):
        """Saves the lock settigs to the remote repository

        Args:
            repo(GitRepository): currently open repository that the file belongs to
        """
        # Save current lockfile
        self._lockFile.save()
        # Stage lockfile changes
        # Must be relitive to worktree root
        repo.index.add(Locking.LOCKFILE_PATH)
        repo.index.write()
        tree = repo.index.write_tree()
        # Commit and push
        repo.commit_push(tree, "MEG LOCKFILE UPDATE")
