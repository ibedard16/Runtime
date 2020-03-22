"""Multimedia Extensible Git (MEG) git repository manager

Git repository manager for runtime
"""

import os
import pathlib
from kivy.logger import Logger
from meg_runtime.config import Config
from meg_runtime.git.repository import GitRepository, GitException


# Git repository manager
class GitManager(dict):
    """Git repository manager"""

    # The git repository manager instance
    __instance = None

    # Git repository manager constructor
    def __init__(self, **kwargs):
        """Git repository manager constructor"""
        # Check if there is already a git repository manager instance
        if GitManager.__instance is not None:
            # Except if another instance is created
            raise GitException(self.__class__.__name__ + " is a singleton!")
        else:
            # Initialize super class constructor
            super().__init__(**kwargs)
            # Set this as the current git repository manager instance
            GitManager.__instance = self

    # Initialize local git repository
    @staticmethod
    def init(repo_path, bare=False, *args, **kwargs):
        """Open local git repository"""
        # Check there is git repository manager instance
        if GitManager.__instance is None:
            GitManager()
        if GitManager.__instance is not None:
            # Log init repo
            Logger.debug(f'MEG Git: Initializing git repository <{repo_path}>')
            try:
                # Initialize the repository
                return GitRepository(repo_path, bare=bare, init=True, *args, **kwargs)
            except Exception as e:
                # Log that opening the repo failed
                Logger.warning(f'MEG Git: {e}')
                Logger.warning(f'MEG Git: Could not open git repository <{repo_path}>')
        return None

    # Open local git repository
    @staticmethod
    def open(repo_path, checkout_branch=None, bare=False, *args, **kwargs):
        """Open local git repository"""
        # Check there is git repository manager instance
        if GitManager.__instance is None:
            GitManager()
        if GitManager.__instance is not None:
            # Log cloning repo
            Logger.debug(f'MEG Git: Opening git repository <{repo_path}>')
            try:
                # Open the repository
                return GitRepository(repo_path, checkout_branch=checkout_branch, bare=bare, *args, **kwargs)
            except Exception as e:
                # Log that opening the repo failed
                Logger.warning(f'MEG Git: {e}')
                Logger.warning(f'MEG Git: Could not open git repository <{repo_path}>')
        return None

    # Clone a remote git repository to a local repository
    @staticmethod
    def clone(repo_url, repo_path=None, checkout_branch=None, bare=False, *args, **kwargs):
        """Clone a remote git repository to a local repository"""
        # Check there is git repository manager instance
        if GitManager.__instance is None:
            GitManager()
        if GitManager.__instance is not None:
            # Log cloning repo
            Logger.debug(f'MEG Git: Cloning git repository <{repo_url}> to <{repo_path}>')
            try:
                # Get the repository path if not provided
                if repo_path is None:
                    # Get the root path in the following order:
                    #  1. The configured repositories directory path
                    #  2. The configured user directory path
                    #  3. The current working directory path
                    repo_prefix = Config.get('path/repos', Config.get('path/user', os.curdir)) + os.sep
                    # Append the name of the repository to the path
                    if isinstance(repo_url, str):
                        repo_path = repo_prefix + pathlib.Path(repo_url).stem
                    elif isinstance(repo_url, pathlib.Path):
                        repo_path = repo_prefix + repo_url.stem
                    else:
                        raise GitException(f'No local repository path was provided and the path could not be determined from the remote <{repo_url}>')
                # Clone the repository by creating a repository instance
                return GitRepository(repo_path, repo_url, checkout_branch=checkout_branch, bare=bare, *args, **kwargs)
            except Exception as e:
                # Log that cloning the repo failed
                Logger.warning(f'MEG Git: {e}')
                Logger.warning(f'MEG Git: Could not clone git repository <{repo_url}> to <{repo_path}>')
        return None

    # Open local git repository or clone a remote git repository to a local repository
    @staticmethod
    def open_or_clone(repo_path, repo_url, checkout_branch=None, bare=False, *args, **kwargs):
        """Open local git repository or clone a remote git repository to a local repository"""
        repo = GitManager.open(repo_path, checkout_branch=checkout_branch, bare=bare, *args, **kwargs)
        if repo is None:
            repo = GitManager.clone(repo_url, repo_path=repo_path, checkout_branch=checkout_branch, bare=bare, *args, **kwargs)
        return repo
