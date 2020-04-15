import pytest
from unittest import mock
import shutil
from meg_runtime.git.locking import Locking
from meg_runtime.git.lockFile import LockFile


@pytest.fixture()
def generateLocking():
    lock = LockFile(Locking.LOCKFILE_PATH)
    lock["project/jeffsPart.dwg"] = "jeff"
    lock["project/jeffs2ndPart.dwg"] = "bob"
    lock["src/other.txt"] = "bob"
    lock.save()
    yield (len(lock), mock.MagicMock())
    shutil.rmtree(".meg")


def test_findLock(generateLocking):
    locking = Locking()
    entry = locking.findLock("project/jeffs2ndPart.dwg")
    assert entry["user"] == "bob"
    entry = locking.findLock("project/jeffsPart.dwg")
    assert entry["user"] == "jeff"
    assert locking.findLock("IOEFJIOFIJEFIOEFJIOEFJIKOEFJOIKEFKOPEFOPKEF") is None


def test_addLock(generateLocking):
    locking = Locking()
    assert not locking.addLock(generateLocking[1], "project/jeffs2ndPart.dwg", "bob")  # Lock belonging to user else already exists
    assert not locking.addLock(generateLocking[1], "project/jeffsPart.dwg", "bob")  # Lock belonging to someone else already exists
    assert locking.addLock(generateLocking[1], "morethings/aThing.svg", "bob")
    assert locking.findLock("morethings/aThing.svg")["user"] == "bob"


def test_removeLock(generateLocking):
    locking = Locking()
    generateLocking[1].permissions = mock.MagicMock()
    generateLocking[1].permissions.can_remove_lock.return_value = False
    assert not locking.removeLock(generateLocking[1], "project/jeffsPart.dwg", "bob")  # Lock belonging to someone else
    assert locking.removeLock(generateLocking[1], "src/other.txt", "bob")
    assert len(locking.locks()) == generateLocking[0] - 1
