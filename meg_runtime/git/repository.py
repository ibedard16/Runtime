"""Git repository"""

from pygit2 import init_repository, clone_repository, Repository


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

    # TODO: Pull the remote repository
    def pull(self, remote_name='origin'):
        pass
