"""Git repository"""

import pygit2
import os
from pygit2 import init_repository, clone_repository, Repository, GitError
from meg_runtime.logger import Logger
from meg_runtime.config import Config
from meg_runtime.git.locking import Locking
from meg_runtime.git.permissions import Permissions


# Git exception
class GitException(Exception):
    """Git exception"""

    # Git exception constructor
    def __init__(self, message, **kwargs):
        """Git exception constructor"""
        super().__init__(message, **kwargs)


# Git repository
class GitRepository(Repository):
    """Git repository"""

    # Git repository constructor
    def __init__(self, path, url=None, checkout_branch=None, bare=False, init=False, *args, **kwargs):
        """Git repository constructor"""
        # Check for special construction
        if init:
            # Initialize a new repository
            self.__dict__ = init_repository(path, bare=bare, workdir_path=path, origin_url=url).__dict__
        elif url is not None:
            # Clone a repository
            self.__dict__ = clone_repository(url, path, bare=bare, checkout_branch=checkout_branch).__dict__
        # Initialize the git repository super class
        super().__init__(path, *args, **kwargs)
        self.__permissions = Permissions(path)
        self.__locking = Locking(self.__permissions, path)

    @property
    def locking(self):
        return self.__locking

    @property
    def permissions(self):
        return self.__permissions

    @property
    def path(self):
        if not self.is_empty:
            path = self.workdir
        else:
            path = super().path
        return os.path.abspath(path)

    # Git repository destructor
    def __del__(self):
        # Free the repository references
        self.free()

    # Fetch remote
    def fetch(self, remote_name='origin'):
        for remote in self.remotes:
            if remote.name == remote_name:
                remote.fetch()

    # Fetch all remotes
    def fetch_all(self):
        for remote in self.remotes:
            remote.fetch()

    def stageChanges(self, username):
        """Adds changes to the index
        Only adds changes allowd by locking and permission module

        Args:
            username(string): username of the git user
        Returns:
            (list(IndexEntry)): list of changed files to specificly not stage, (used to revert changes before merge)
        """
        self.index.add_all()
        entriesToAdd = []
        entriesToNotAdd = []
        for changedFile in self.index:
            lockEntry = self.__locking.findLock(changedFile.path)
            if (((lockEntry is None or lockEntry["user"] == username) and self.__permissions.can_write(username, changedFile.path)) or
                    changedFile.path == Locking.LOCKFILE_PATH or changedFile.path == Permissions.PERMISSION_PATH):
                entriesToAdd.append(changedFile)
            else:
                entriesToNotAdd.append(changedFile)
        self.index.read(force=True)
        for entry in entriesToAdd:
            self.index.add(entry)
        self.index.write()
        return entriesToNotAdd

    def pullPaths(self, paths):
        """Checkout only the files in the list of paths

        Args:
            paths (list(stirng)): paths to checkout
        Returns:
            (bool): Were the paths sucessfuly checkedout
        """
        self.fetch_all()
        fetch_head = self.lookup_reference('FETCH_HEAD')
        if fetch_head is not None:
            try:
                self.head.set_target(fetch_head.target)
                self.checkout_head(paths=paths)
                return True
            except GitError as e:
                Logger.warning(f'MEG Repositiory: {e}')
        Logger.warning(f'MEG Repositiory: Could not checkout paths')
        return False

    def pull(self, remote_name='origin', fail_on_conflict=False, username=None, password=None):
        """Pull and merge
        Merge is done fully automaticly, currently uses 'ours' on conflicts

        Args:
            remote_ref_name (string): name of reference to the remote being pulled from
        """
        if username is None:
            username = Config.get('user/username')
        if password is None:
            password = Config.get('user/password')
        self.__permissions.save()
        self.__locking.save()
        # Find state of both references have
        self.fetch_all()
        remoteId = self.lookup_reference("FETCH_HEAD").resolve().target
        localId = self.lookup_reference("HEAD").resolve().target
        ahead, behind = self.ahead_behind(localId, remoteId)
        # Pull only required if we are behind
        if behind > 0:
            # If changes, commit and prepare for merge
            if self.isChanged(username):
                self.stageChanges(username)
                self.create_commit('HEAD', self.default_signature, self.default_signature, "MEG PULL OWN", self.index.write_tree(), [self.head.target])
            # Find the kind of required merge
            mergeState, _ = self.merge_analysis(remoteId)
            # Preform merge
            if mergeState & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
                # Fastforward and checkout remote
                self.checkout_tree(self.get(remoteId))
                self.head.set_target(remoteId)
                self.checkout_head()
            elif mergeState & pygit2.GIT_MERGE_ANALYSIS_NORMAL:
                # Preform painful merge
                if fail_on_conflict:
                    self.state_cleanup()
                    return False
                # Find files not to staged (because lock, permissions,...) and discard changes so merging can occur
                badPaths = [entry.path for entry in self.stageChanges(username)]
                self.checkout_head(strategy=pygit2.GIT_CHECKOUT_FORCE, paths=badPaths)
                # Merge will stage changes automaticly and find conflicts
                self.merge(remoteId)
                if self.index.conflicts is not None:
                    self.resolveLockingPermissionsMerge()
                    self.resolveGeneralMerge(username)
                else:
                    self.__permissions.load()
                    self.__locking.load()
                # Check there are no merge conflicts before committing
                if self.index.conflicts is None or len(self.index.conflicts) == 0:
                    # Commit the merge
                    self.index.add_all()
                    self.create_commit('HEAD', self.default_signature, self.default_signature, "MEG MERGE", self.index.write_tree(), [self.head.target, remoteId])
                self.push(remote_name, username, password)
            self.state_cleanup()
        return True

    def resolveLockingPermissionsMerge(self):
        """Resolve conflicts on the locking or permissions files
        """
        resolved_conflicts = []
        for conflict in self.index.conflicts:
            path = self.pathFromConflict(conflict)
            # For conflicting Locks or Permissions that have been changed on remote, it is safest to discard local version and accept the remote
            # Then reload the respective modules
            if path == Locking.LOCKFILE_PATH or path == Permissions.PERMISSION_PATH:
                self.writeConflictResolution(conflict[2], path)
        self.__locking.load()
        self.__permissions.load()
        # Remove all resolved conflicts
        for conflict in resolved_conflicts:
            del self.index.conflicts[conflict]

    def resolveGeneralMerge(self, username):
        """Resolve all remaining conflicts
        TODO: Some other merge logic from plugins and other stuff
        """
        # Resolve remaining conflicts
        resolved_conflicts = []
        for conflict in self.index.conflicts:
            path = self.pathFromConflict(conflict)
            if not self.__permissions.can_write(username, path):
                # Not allowed to write, use theirs
                self.writeConflictResolution(conflict[2], path)
            elif not self.__locking.findLock(path) is None:
                if self.__locking.findLock(path)["user"] != username:
                    # Is locked by not the local user, use theirs
                    self.writeConflictResolution(conflict[2], path)
                else:
                    # Else its our lock
                    self.writeConflictResolution(conflict[1], path)
            else:
                # TODO: Some other merge logic from plugins and other stuff
                # Currently just use ours
                self.writeConflictResolution(conflict[1], path)
            # Add path to resolve conflict
            resolved_conflicts.append(path)
        # Remove all resolved conflicts
        for conflict in resolved_conflicts:
            del self.index.conflicts[conflict]

    def writeConflictResolution(self, indexEntry, path):
        """For simple merge conflict resolution, writes contentes of index entry to file
        Or deletes the file if required.
        """
        if indexEntry is None:
            if os.path.exists(path):
                os.remove(path)
        else:
            open(os.path.join(self.path, path), "w+b").write(self.get(indexEntry.id).data)

    def pathFromConflict(self, indexConflict):
        """Returns path of conflict from index.conflicts entry
        """
        return [conf.path for conf in indexConflict if conf is not None][0]

    def push(self, remote_name='origin', username=None, password=None):
        """Pushes current commits
        4/13/20 21 - seems to be working

        Args:
            remote_name (string, optional): name of the remote to push to
            username (string, optional): username of user account used for pushing
            password (string, optional): password of user account used for pushing
        """
        if username is None:
            username = Config.get('user/username')
        if password is None:
            password = Config.get('user/password')
        creds = pygit2.UserPass(username, password)
        remote = self.remotes[remote_name]
        remote.credentials = creds
        try:
            remote.push([self.head.name], callbacks=pygit2.RemoteCallbacks(credentials=creds))
        except GitError as e:
            Logger.warning(e)
            Logger.warning("MEG Git Repository: Failed to push commit")

    def commit_push(self, tree, message, remote_name='origin', username=None, password=None):
        """Commits and pushes staged changes in the tree
        TODO: Ensure that the config keys are correct
        4/13/20 21 - seems to be working

        Args:
            tree (Oid): Oid id created from repositiory index (ex: repo.index.write_tree()) containing the tracked file changes (proably)
            message (string): commit message
            remote_name (string, optional): name of the remote to push to
            username (string, optional): username of user account used for pushing
            password (string, optional): password of user account used for pushing
        """
        if username is None:
            username = Config.get('user/username')
        if password is None:
            password = Config.get('user/password')
        # Create commit on current branch, parent is current commit, author and commiter is the default signature
        self.create_commit(self.head.name, self.default_signature, self.default_signature, message, tree, [self.head.target])
        self.push(remote_name, username, password)

    def isChanged(self, username):
        """Are there local changes from the last commit
        Only counts changes alowed by locking and permission module commitable files
        """
        mask = pygit2.GIT_STATUS_WT_DELETED | pygit2.GIT_STATUS_WT_RENAMED | pygit2.GIT_STATUS_WT_MODIFIED | pygit2.GIT_STATUS_WT_NEW
        for path, status in self.status().items():
            if status & mask == 0:
                continue
            lockEntry = self.__locking.findLock(path)
            if (((lockEntry is None or lockEntry["user"] == Config.get('user/username')) and self.__permissions.can_write(username, path)) or
                    path == Locking.LOCKFILE_PATH or path == Permissions.PERMISSION_PATH):
                return True
        return False

    def sync(self, remote_name='origin', username=None, password=None):
        """Pulls and then pushes, merge conflicts resolved by pull

        Args:
            username (string, optional): username of user account used for pushing
            password (string, optional): password of user account used for pushing
        """
        if username is None:
            username = Config.get('user/username')
        if password is None:
            password = Config.get('user/password')
        self.__permissions.save()
        self.__locking.save()
        self.pull(remote_name, username=username, password=password)
        if self.isChanged(username):
            self.stageChanges(username)
            self.create_commit('HEAD', self.default_signature, self.default_signature, "MEG SYNC", self.index.write_tree(), [self.head.target])
            self.push(remote_name, username=username, password=password)
