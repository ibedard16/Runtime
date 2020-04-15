"""MEG system file locking

To be used to lock files, unlock files, override locks, and view locks
Will confirm user roles and preform required git operations

All file paths are relitive to the repository directory
Working directory should be changed by the git module
"""

from meg_runtime.locking.lockFile import LockFile
from meg_runtime.logger import Logger


class LockingManager:
    """Used to prefrom all locking operations
    To be used to lock files, unlock files, override locks, and view locks
    Will confirm user roles and preform required git operations
    """
    LOCKFILE_PATH = ".meg/locks.json"
    __instance = None

    def __init__(self):
        if LockingManager.__instance is not None:
            raise Exception("Trying to create a second instance of LockingManager, which is a singleton")
        else:
            LockingManager.__instance = self
            LockingManager.__instance._lockFile = LockFile(LockingManager.LOCKFILE_PATH)

    @staticmethod
    def addLock(repo, filepath, username):
        """Sync the repo, adds the lock, sync the repo
        Args:
            repo (GitRepository): currently open repository that the file belongs to
            filepath (string): path to the file to lock
            username (string): username of current user
        Returns:
            (bool): was lock successfully added
        """
        if LockingManager.__instance is None:
            LockingManager()
        if not repo.permissions.can_lock(username):
            return False
        LockingManager.__instance.pullLocks(repo)
        if filepath in LockingManager.__instance._lockFile:
            return False
        else:
            LockingManager.__instance._lockFile[filepath] = username
            LockingManager.__instance.pushLocks(repo)
            return True

    @staticmethod
    def removeLock(repo, filepath, username):
        """Sync the repo, remove a lock from a file, and sync again
        Args:
            repo (GitRepository): currently open repository that the file belongs to
            filepath (string): path to file to unlock
            username (string): username of current user
        Returns:
            (bool): is there still a lock (was the user permitted to remove the lock)
        """
        if LockingManager.__instance is None:
            LockingManager()
        LockingManager.__instance.pullLocks(repo)
        lock = LockingManager.__instance._lockFile[filepath]
        if(lock is None):
            return True
        elif(lock["user"] == username or repo.permissions.can_remove_lock(username)):
            del LockingManager.__instance._lockFile[filepath]
        else:
            return False
        LockingManager.__instance.pushLocks(repo)
        return True

    @staticmethod
    def findLock(filepath):
        """Find if there is a lock on the file, does not automatily sync the lock file
        Args:
            filepath (string): path of file to look for
        Returns:
            (dictionary): lockfile entry for the file
            (None): There is no entry
        """
        if LockingManager.__instance is None:
            LockingManager()
        LockingManager.__instance._lockFile.load()
        return LockingManager.__instance._lockFile[filepath]

    @staticmethod
    def locks():
        """Get the LockFile object
        """
        LockingManager.__instance._lockFile.load()
        return LockingManager.__instance._lockFile

    @staticmethod
    def pullLocks(repo):
        """Pulls the lock file from remote and loads it

        Args:
            repo(GitRepository): currently open repository that the file belongs to
        """
        if LockingManager.__instance is None:
            LockingManager()
        if repo is None:
            Logger.warning("MEG Locking: Could not open repositiory")
            return False
        # Fetch current version
        if not repo.pullPaths([LockingManager.LOCKFILE_PATH]):
            Logger.warning("MEG Locking: Could not download newest lockfile")

        LockingManager.__instance._lockFile.load()

    @staticmethod
    def pushLocks(repo):
        """Saves the lock settigs to the remote repository

        Args:
            repo(GitRepository): currently open repository that the file belongs to
        """
        if LockingManager.__instance is None:
            LockingManager()
        # Save current lockfile
        LockingManager.__instance._lockFile.save()
        # Stage lockfile changes
        # Must be relitive to worktree root
        repo.index.add(LockingManager.LOCKFILE_PATH)
        repo.index.write()
        tree = repo.index.write_tree()
        # Commit and push
        repo.commit_push(tree, "MEG LOCKFILE UPDATE")
