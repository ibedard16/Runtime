import pytest
import os
import shutil
from meg_runtime.git.lockFile import LockFile


@pytest.fixture()
def generateLockfile():
    fileName = ".meg/templockfile"
    LockFile(fileName)  # Generate lockfile
    yield fileName
    if os.path.exists(".meg"):
        shutil.rmtree(".meg")


@pytest.fixture()
def loadEmptyFile():
    filepath = "./emptyFile"
    yield filepath
    if os.path.exists(filepath):
        os.remove(filepath)


def test_load(generateLockfile, loadEmptyFile):
    lock = LockFile(generateLockfile)
    lock["project/jeffsPart.dwg"] = "jeff"
    lock.load(loadEmptyFile)
    assert len(lock) == 0


def test_locks(generateLockfile):
    lock = LockFile(generateLockfile)
    lock["project/jeffsPart.dwg"] = "jeff"
    lock["project/jeffs2ndPart.dwg"] = "jeff"
    assert len(lock) == 2


def test_addLock(generateLockfile):
    lock = LockFile(generateLockfile)
    lock["project/jeffsPart.dwg"] = "jeff"
    lock["project/jeffs2ndPart.dwg"] = "bob"
    assert lock["project/jeffsPart.dwg"]["user"] == "jeff"
    assert lock["project/jeffs2ndPart.dwg"]["user"] == "bob"


def test_removeLock(generateLockfile):
    lock = LockFile(generateLockfile)
    lock["project/jeffsPart.dwg"] = "jeff"
    lock["project/jeffs2ndPart.dwg"] = "bob"
    del lock["project/jeffsPart.dwg"]
    del lock["nonExistantLock"]  # should not error
    assert len(lock) == 1
    assert not lock["project/jeffs2ndPart.dwg"] is None


def test_findLock(generateLockfile):
    lock = LockFile(generateLockfile)
    lock["project/jeffsPart.dwg"] = "jeff"
    lock["project/jeffs2ndPart.dwg"] = "bob"
    entry = lock["project/jeffs2ndPart.dwg"]
    assert entry["user"] == "bob"
