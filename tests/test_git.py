"""Runtime library unit testing for git"""

import os
import time
import shutil
import tempfile
import pytest
from dateutil.tz import gettz
from datetime import datetime
from kivy.logger import Logger
from meg_runtime import GitRepository, GitManager


# PyTest session fixture to get temporary path for git repo tests
@pytest.fixture(scope='session')
def temp_session_repo_path():
    """PyTest session fixture to get temporary path for git repo tests"""
    # Get a temporary repository path
    repo_path = tempfile.mkdtemp()
    # Yield the temporary repository path
    yield repo_path
    # After session remove the remove repository path
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, True)


# PyTest fixture to get temporary path for git repo tests
@pytest.fixture()
def temp_repo_path():
    """PyTest session fixture to get temporary path for git repo tests"""
    # Get a temporary repository path
    repo_path = tempfile.mkdtemp()
    # Yield the temporary repository path
    yield repo_path
    # After remove the remove repository path
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, True)


# Test cloning a repository
def test_git_clone(temp_session_repo_path):
    # The repository URL
    repo_url = 'https://github.com/MultimediaExtensibleGit/Runtime.git'
    # repo_url = 'ssh://github.com/MultimediaExtensibleGit/Runtime.git'
    # Clone the repository
    repo = GitManager.clone(repo_url, temp_session_repo_path)
    # Check the repository was successfully cloned
    assert repo is not None
    assert not repo.is_bare
    assert not repo.is_empty


# Test opening a repository
def test_git_open(temp_session_repo_path):
    # Open the repository
    repo = GitManager.open(temp_session_repo_path)
    # Check the repository was successfully opened
    assert repo is not None
    assert not repo.is_bare
    assert not repo.is_empty


# Test repository checkout
def test_git_checkout(temp_session_repo_path):
    # Open the repository
    repo = GitRepository(temp_session_repo_path)
    # Check the repository was opened
    assert repo is not None
    assert not repo.is_bare
    repo.checkout('refs/remotes/origin/staging')
    assert not repo.is_empty


# Test repository log
def test_git_log(temp_session_repo_path):
    # Open the repository
    repo = GitRepository(temp_session_repo_path)
    # Check the repository was opened
    assert repo is not None
    assert not repo.is_bare
    assert not repo.is_empty
    # Print the repository last commit log
    commit = repo[repo.head.target]
    Logger.info('MEG Git: commit ' + str(commit.tree_id))
    Logger.info('MEG Git: Author: ' + commit.author.name + ' <' + commit.author.email + '>')
    Logger.info('MEG Git: Date:   ' + datetime.fromtimestamp(commit.commit_time, tz=gettz(time.tzname[time.daylight])).strftime('%c %z'))
    Logger.info('MEG Git: ' + commit.message)


# Test opening a repository
def test_git_init(temp_repo_path):
    # Open the repository
    repo = GitManager.init(temp_repo_path)
    # Check the repository was successfully initialized
    assert repo is not None
    assert not repo.is_bare
    assert repo.is_empty
