"""Git repository"""

import pygit2
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
        self.permissions = Permissions()
        self.locking = Locking(self)
        # Initialize the git repository super class
        super().__init__(path, *args, **kwargs)

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

    def pullPermissions(self, username):
        """Pull down current version of permissions file
        """
        if not self.pullPath([Permissions.PERMISSION_PATH]):
            Logger.warning("MEG repository: Failed to download permission file")
        self.permissions = Permissions()

    def pushPermissions(self):
        """Save permissions file and push to repo
        """
        # Store permissions in file
        self.permissions.save()
        # stage permissions file
        self.index.add(Permissions.PERMISSION_PATH)
        self.index.write()
        # Commit and push
        self.commit_push(self.index.write_tree(), "MEG PERMISSIONS UPDATE")

    def stageChanges(self, username=Config.get('user/username')):
        """Adds changes to the index
        Only adds changes allowd by locking and permission module
        """
        self.index.add_all()
        entriesToAdd = []
        for changedFile in self.index:
            lockEntry = self.locking.findLock(changedFile.path)
            if (lockEntry is None or lockEntry["user"] == username) and self.permissions.can_write(username, changedFile.path):
                entriesToAdd.append(changedFile)
        self.index.read(force=True)
        for entry in entriesToAdd:
            self.index.add(entry)
        self.index.write()

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

    def pull(self, remote_name='origin', fail_on_conflict=False, username=Config.get('user/username'), password=Config.get('user/password')):
        """Pull and merge
        Merge is done fully automaticly, currently uses 'ours' on conflicts
        TODO: Preform a proper merge with the locking used to resolve conflicts
        4/13/20 21 - seems to be working for both merge types

        Args:
            remote_ref_name (string): name of reference to the remote being pulled from
        """
        self.fetch_all()
        self.permissions.save()
        # Find and stage changes that are allowd by locking system
        if self.isChanged(username):
            self.stageChanges(username)
            self.create_commit('HEAD', self.default_signature, self.default_signature, "MEG PULL OWN", self.index.write_tree(), [self.head.target])
        # Prepare for a merge
        remoteId = self.lookup_reference("FETCH_HEAD").target
        mergeState, _ = self.merge_analysis(remoteId)
        if mergeState & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
            # Fastforward and checkout remote
            self.checkout_tree(self.get(remoteId))
            self.head.set_target(remoteId)
            self.checkout_head()
        elif mergeState & pygit2.GIT_MERGE_ANALYSIS_NORMAL:
            # Preform merge
            if fail_on_conflict:
                self.state_cleanup()
                return False
            self.preformMerge(remoteId, username)
        self.state_cleanup()
        self.permissions = Permissions()
        return True

    def preformMerge(self, remoteId, username=Config.get('user/username')):
        """Merge and commit
        """
        # Merge will stage changes automaticly and find conflicts
        self.merge(remoteId)
        for conflict in self.index.conflicts:
            path = self.pathFromConflict(conflict)
            if not self.permissions.can_write(username, conflict[0].path):
                # Not allowed to write, use theirs
                self.stageConflictChange(conflict[2], path)
            elif not self.locking.findLock(path) is None:
                if self.locking.findLock(path)["user"] != username:
                    # Is locked by not the local user, use theirs
                    self.stageConflictChange(conflict[2], path)
                else:
                    # Else its our lock
                    self.stageConflictChange(conflict[1], path)
            elif path == Locking.LOCKFILE_PATH:
                oldLocks = None if conflict[0] is None else Locking(self, conflict[0].data)
                remoteLocks = None if conflict[1] is None else Locking(self, conflict[1].data)
                self.locking.merge(oldLocks, remoteLocks)
                del self.index.conflicts[path]
                self.index.add(path)
            elif path == Permissions.PERMISSION_PATH:
                # For conflicting Permissions that have been changed on remote, it is safest to discard local version and accept the remote
                self.stageConflictChange(conflict[2], path)
            else:
                # TODO: Some other merge logic from plugins and other stuff
                # Currently just use ours
                if not conflict[1] is None:
                    self.index.add(conflict[1])
                else:
                    self.index.remove(path)
                del self.index.conflicts[path]
        # Commit the merge
        self.create_commit('HEAD', self.default_signature, self.default_signature, "MEG MERGE", self.index.write_tree(), [self.head.target, remoteId])

        def stageConflictChange(self, indexEntry, path):
            if indexEntry is not None:
                self.index.add(indexEntry)
            else:
                self.index.remove(path)
            del self.index.conflicts[path]

    def pathFromConflict(self, indexConflict):
        """Returns path of conflict from index.conflicts entry
        """
        return [conf.path for conf in indexConflict if conf is not None][0]

    def push(self, remote_name='origin', username=Config.get('user/username'), password=Config.get('user/password')):
        """Pushes current commits
        4/13/20 21 - seems to be working

        Args:
            remote_name (string, optional): name of the remote to push to
            username (string, optional): username of user account used for pushing
            password (string, optional): password of user account used for pushing
        """
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
        # Create commit on current branch, parent is current commit, author and commiter is the default signature
        self.create_commit(self.head.name, self.default_signature, self.default_signature, message, tree, [self.head.target])
        self.push(remote_name, username, password)

    def isChanged(self, username=Config.get('user/username')):
        """Are there local changes from the last commit
        Only counts changes alowed by locking and permission module commitable files
        """
        for diff in self.index.diff_to_workdir():
            lockEntry = self.locking.findLock(diff.delta.old_file.path)
            if (lockEntry is None or lockEntry["user"] == Config.get('user/username')) and self.permissions.can_write(username, diff.delta.old_file.path):
                return True
        return False

    def sync(self, remote_name='origin', username=Config.get('user/username'), password=Config.get('user/password')):
        """Pulls and then pushes, merge conflicts resolved by pull

        Args:
            username (string, optional): username of user account used for pushing
            password (string, optional): password of user account used for pushing
        """
        self.pull(remote_name, username=username, password=password)
        self.push(remote_name, username=username, password=password)
