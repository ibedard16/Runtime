import pytest
from unittest import mock
import shutil
from meg_runtime.git.locking import Locking
import os


@pytest.fixture("module")
def generateLockFile():
    lock = Locking(mock.MagicMock(), ".")
    lock.save()
    yield
    if os.path.exists(".meg"):
        shutil.rmtree(".meg")


@pytest.fixture()
def populateLocks():
    permissionsMock = mock.MagicMock()
    permissionsMock.can_remove_lock.return_value = False
    permissionsMock.can_lock.return_value = True
    lock = Locking(permissionsMock, ".")
    lock.clear()
    lock.addLock("jeff", "project/jeffsPart.dwg")
    lock.addLock("bob", "project/jeffs2ndPart.dwg")
    lock.addLock("bob", "src/other.txt")
    return lock


def test_load(populateLocks):
    print("TEST LOAD: " + str(len(populateLocks)))
    populateLocks.save()
    print("TEST LOAD: " + str(len(populateLocks)))
    populateLocks.load()
    print("TEST LOAD: " + str(len(populateLocks)))
    assert "src/other.txt" in populateLocks
    assert "potato" not in populateLocks
    populateLocks.clear()
    assert "src/other.txt" not in populateLocks


def test_loads(populateLocks):
    populateLocks.loads(r'{"potato": {"user": "jeff", "time": 5}}')
    assert "potato" in populateLocks
    assert "src/other.txt" not in populateLocks


def test_findLock(populateLocks):
    entry = populateLocks.findLock("project/jeffs2ndPart.dwg")
    assert entry["user"] == "bob"
    entry = populateLocks.findLock("project/jeffsPart.dwg")
    assert entry["user"] == "jeff"
    assert populateLocks.findLock("IOEFJIOFIJEFIOEFJIOEFJIKOEFJOIKEFKOPEFOPKEF") is None


def test_addLock():
    permissionsMock = mock.MagicMock()
    permissionsMock.can_lock.return_value = True
    locking = Locking(permissionsMock, ".")
    locking.clear()
    assert locking.addLock("jeff", "project/jeffsPart.dwg")
    assert not locking.addLock("bob", "project/jeffsPart.dwg")  # Lock belonging to someone else already exists
    assert locking.addLock("bob", "morethings/aThing.svg")
    assert locking.findLock("morethings/aThing.svg")["user"] == "bob"


def test_removeLock(populateLocks):
    populateLocks._Locking__permissions.can_remove_lock.return_value = False
    numberOfLocks = len(populateLocks)
    assert not populateLocks.removeLock("bob", "project/jeffsPart.dwg")  # Lock belonging to someone else
    assert populateLocks.removeLock("bob", "src/other.txt")
    assert len(populateLocks) == numberOfLocks - 1
    populateLocks._Locking__permissions.can_remove_lock.return_value = True
    assert populateLocks.removeLock("bob", "project/jeffsPart.dwg")
    assert len(populateLocks) == numberOfLocks - 2


def test_addLocks(populateLocks):
    assert populateLocks.addLocks("joe", ["potato.txt", "thing/a.out", "niceHat"])
    assert "niceHat" in populateLocks
    assert not populateLocks.addLocks("joe", ["project/jeffsPart.dwg", "spoons.jpg"])
    assert "spoons.jpg" not in populateLocks


def test_removeLockByUser(populateLocks):
    populateLocks.removeLocksByUser("bob")
    assert "src/other.txt" not in populateLocks
    assert "project/jeffsPart.dwg" in populateLocks
