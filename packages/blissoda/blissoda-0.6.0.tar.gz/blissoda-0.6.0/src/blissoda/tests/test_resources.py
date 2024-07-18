import pytest
from .. import resources


def test_existing():
    with resources.resource_path("exafs", "exafs.ows") as path:
        assert path.is_file()

    assert str(path) == resources.resource_filename("exafs", "exafs.ows")


def test_non_existing():
    with pytest.raises(FileNotFoundError):
        with resources.resource_path("exafs", "notexisting.ows"):
            pass

    with pytest.raises(FileNotFoundError):
        resources.resource_filename("exafs", "notexisting.ows")


def test_not_a_file():
    with pytest.raises(FileNotFoundError):
        with resources.resource_path("exafs"):
            pass

    with pytest.raises(FileNotFoundError):
        resources.resource_filename("exafs")
