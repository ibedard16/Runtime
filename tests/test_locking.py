import pytest
from unittest import mock
import shutil
from meg_runtime.locking import LockingManager
from meg_runtime.locking.lockFile import LockFile


@pytest.fixture()
def generateLocking():
    lock = LockFile(LockingManager.LOCKFILE_PATH)
    lock["project/jeffsPart.dwg"] = "jeff"
    lock["project/jeffs2ndPart.dwg"] = "bob"
    lock["src/other.txt"] = "bob"
    lock.save()
    LockingManager._LockingManager__instance = None
    LockingManager()
    yield (len(lock), mock.MagicMock())
    shutil.rmtree(".meg")


def test_findLock(generateLocking):
    entry = LockingManager.findLock("project/jeffs2ndPart.dwg")
    assert entry["user"] == "bob"
    entry = LockingManager.findLock("project/jeffsPart.dwg")
    assert entry["user"] == "jeff"
    assert LockingManager.findLock("IOEFJIOFIJEFIOEFJIOEFJIKOEFJOIKEFKOPEFOPKEF") is None


def test_addLock(generateLocking):
    assert not LockingManager.addLock(generateLocking[1], "project/jeffs2ndPart.dwg", "bob")  # Lock belonging to user else already exists
    assert not LockingManager.addLock(generateLocking[1], "project/jeffsPart.dwg", "bob")  # Lock belonging to someone else already exists
    assert LockingManager.addLock(generateLocking[1], "morethings/aThing.svg", "bob")
    assert LockingManager.findLock("morethings/aThing.svg")["user"] == "bob"


def test_removeLock(generateLocking):
    generateLocking[1].permissions = mock.MagicMock()
    generateLocking[1].permissions.can_remove_lock.return_value = False
    assert not LockingManager.removeLock(generateLocking[1], "project/jeffsPart.dwg", "bob")  # Lock belonging to someone else
    assert LockingManager.removeLock(generateLocking[1], "src/other.txt", "bob")
    assert len(LockingManager.locks()) == generateLocking[0] - 1
