def test_getWarning():
    version01 = Version("1.2.3")
    version02 = Version("1.2.6")

    version11 = Version("1.2.3-b1")
    version12 = Version("1.2.3-b2")

    version21 = Version("1.2.3-a1")
    version22 = Version("1.2.3-a2")

    assert version01.getWarning(version02) == "Version 1.2.3 is older than Version 1.2.6"
    assert version11.getWarning(version12) == "Version 1.2.3 Beta 1 is older than Version 1.2.3 Beta 2"
    assert version21.getWarning(version22) == "Version 1.2.3 Alpha 1 is older than Version 1.2.3 Alpha 2"
    assert version21.getWarning(version11) == "Version 1.2.3 Alpha 1 is older than Version 1.2.3 Beta 1"

def test_no_channels():
    version01 = Version("1.2.3")
    version02 = Version("1.2.6")

    assert version01 == version01
    assert version01 < version02
    assert version01 <= version02
    assert version02 > version01
    assert version02 >= version01
    assert version01 != version02

def test_channels():
    version01 = Version("1.2.3")
    version11 = Version("1.2.3-b1")
    version12 = Version("1.2.3-b2")
    version21 = Version("1.2.3-a1")
    version22 = Version("1.2.3-a2")

    # Test within the same channel
    assert version11 == version11
    assert version11 < version12
    assert version11 <= version12
    assert version12 > version11
    assert version12 >= version11
    assert version11 != version12

    assert version21 == version21
    assert version21 < version22
    assert version21 <= version22
    assert version22 > version21
    assert version22 >= version21
    assert version21 != version22

    # Test between channels (beta > alpha)
    assert version11 > version21
    assert version11 >= version21
    assert version21 < version11
    assert version21 <= version11
    assert version11 != version21

    # Test between channels (beta < release), (alpha < release)
    assert version11 < version01
    assert version11 <= version01
    assert version01 > version11
    assert version01 >= version11
    assert version11 != version01

    assert version21 < version01
    assert version21 <= version01
    assert version01 > version21
    assert version01 >= version21
    assert version21 != version01
    
    

import pytest
from versions.versions import Version, releaseTypes

@pytest.fixture
def version_basic():
    return Version("1.2.3")

@pytest.fixture
def version_with_appendage():
    return Version("1.2.3-a4")

@pytest.fixture
def version_tuple_basic():
    return (1, 2, 3, "")

@pytest.fixture
def version_tuple_with_appendage():
    return (1, 2, 3, "a4")

def test_fromTuple(version_tuple_basic):
    version = Version.fromTuple(version_tuple_basic)
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.appendage == ""

def test_fromTuple_with_appendage(version_tuple_with_appendage):
    version = Version.fromTuple(version_tuple_with_appendage)
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.appendage == "a4"

def test_toTuple(version_basic, version_tuple_basic):
    version_tuple = version_basic.toTuple()
    assert version_tuple == version_tuple_basic

def test_toTuple_with_appendage(version_with_appendage, version_tuple_with_appendage):
    version_tuple = version_with_appendage.toTuple()
    assert version_tuple == version_tuple_with_appendage

def test_str(version_basic, version_with_appendage):
    assert str(version_basic) == "Version 1.2.3"
    assert str(version_with_appendage) == "Version 1.2.3 Alpha 4"

def test_repr(version_basic, version_with_appendage):
    assert repr(version_basic) == "1.2.3"
    assert repr(version_with_appendage) == "1.2.3-a4"

def test_hash(version_basic, version_with_appendage):
    assert hash(version_basic) == hash(str(version_basic))
    assert hash(version_with_appendage) == hash(str(version_with_appendage))

def test_fromDict():
    version_dict = {
        "major": 1,
        "minor": 2,
        "patch": 3,
        "releaseType": releaseTypes.RELEASE,
        "revision": 0
    }
    version = Version.fromDict(version_dict)
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.appendage == ""

def test_fromDict_with_appendage():
    version_dict = {
        "major": 1,
        "minor": 2,
        "patch": 3,
        "releaseType": releaseTypes.ALPHA,
        "revision": 4
    }
    version = Version.fromDict(version_dict)
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.appendage == "a4"

def test_toDict_with_appendage(version_with_appendage):
    version_dict = version_with_appendage.toDict()
    assert version_dict["major"] == 1
    assert version_dict["minor"] == 2
    assert version_dict["patch"] == 3
    assert version_dict["releaseType"] == releaseTypes.ALPHA
    assert version_dict["revision"] == 4

def test_toDict(version_basic):
    version_dict = version_basic.toDict()
    assert version_dict["major"] == 1
    assert version_dict["minor"] == 2
    assert version_dict["patch"] == 3
    assert version_dict["releaseType"] == releaseTypes.RELEASE
    assert version_dict["revision"] == 0

def test_toList(version_basic):
    version_list = version_basic.toList()
    assert version_list == [1, 2, 3, ""]

def test_toList_with_appendage(version_with_appendage):
    version_list = version_with_appendage.toList()
    assert version_list == [1, 2, 3, "a4"]

def test_fromList():
    version = Version.fromList([1, 2, 3, ""])
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.appendage == ""

def test_fromList_with_appendage():
    version = Version.fromList([1, 2, 3, "a4"])
    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.appendage == "a4"

# Additional tests for getWarning and comparisons would follow a similar pattern,
# using fixtures for setup and assert statements for validation.