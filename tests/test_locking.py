import pytest
from unittest import mock
import os
from meg_runtime.locking import LockingManager
from meg_runtime.locking.lockFile import LockFile


@pytest.fixture()
def generateLocking():
    lock = LockFile(LockingManager.LOCKFILE_DIR + LockingManager.LOCKFILE_NAME)
    lock["project/jeffsPart.dwg"] = "jeff"
    lock["project/jeffs2ndPart.dwg"] = "bob"
    lock["src/other.txt"] = "bob"
    lock.save()
    LockingManager._LockingManager__instance = None
    LockingManager()
    yield len(lock)
    os.remove(LockingManager.LOCKFILE_DIR + LockingManager.LOCKFILE_NAME)
    os.rmdir(LockingManager.LOCKFILE_DIR)

def test_findLock(generateLocking):
    entry = LockingManager.findLock("project/jeffs2ndPart.dwg")
    assert entry["user"] == "bob"
    entry = LockingManager.findLock("project/jeffsPart.dwg")
    assert entry["user"] == "jeff"
    assert LockingManager.findLock("IOEFJIOFIJEFIOEFJIOEFJIKOEFJOIKEFKOPEFOPKEF") is None

def test_addLock(generateLocking):
    assert not LockingManager.addLock("project/jeffs2ndPart.dwg", "bob") #Lock belonging to user else already exists
    assert not LockingManager.addLock("project/jeffsPart.dwg", "bob") #Lock belonging to someone else already exists
    assert LockingManager.addLock("morethings/aThing.svg", "bob")
    assert LockingManager.findLock("morethings/aThing.svg")["user"] == "bob"

def test_removeLock(generateLocking):
    assert LockingManager.removeLock("project/jeffsPart.dwg", "bob") == False #Lock belonging to someone else
    assert LockingManager.removeLock("src/other.txt", "bob") == True
    assert len(LockingManager.locks()) == generateLocking - 1

