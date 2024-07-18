import numpy
import pytest

try:
    from ..persistent.ordereddict import PersistentOrderedDict
except TypeError:
    # bliss not installed
    PersistentOrderedDict = None
from ..persistent.ndarray import PersistentNdArray
from ..persistent.parameters import WithPersistentParameters


def test_persistent_parameters(mock_persistent):
    class MyParameters(WithPersistentParameters, parameters=["a", "b"]):
        def __init__(self, **defaults) -> None:
            defaults.setdefault("a", 1)
            super().__init__(**defaults)

    parameters = MyParameters()

    expected = {"a": 1}
    assert mock_persistent == expected
    assert parameters.a == 1
    assert parameters.b is None

    parameters.a = 2
    expected["a"] = 2
    assert mock_persistent == expected
    assert parameters.a == 2

    parameters = MyParameters()
    assert parameters.a == 2

    parameters.a = None
    expected["a"] = None
    assert mock_persistent == {"a": None}
    assert parameters.a is None
    assert parameters.b is None


def test_persistent_parameters_dict(mock_persistent):
    class MyParameters(WithPersistentParameters, parameters=["python_dict"]):
        def __init__(self, **defaults) -> None:
            defaults.setdefault("python_dict", dict())
            super().__init__(**defaults)

    parameters = MyParameters()
    expected = {}

    assert mock_persistent == {"python_dict": expected}
    assert parameters.python_dict == expected

    parameters.python_dict["a"] = 2
    parameters.python_dict["fix"] = -1
    expected["python_dict"] = {"a": 2, "fix": -1}
    assert mock_persistent == expected
    assert parameters.python_dict == expected["python_dict"]

    parameters.python_dict["a"] = {"x": 1, "fix": -2}
    expected["python_dict"]["a"] = {"x": 1, "fix": -2}
    assert mock_persistent == expected
    assert parameters.python_dict["a"]["x"] == 1

    parameters.python_dict["a"]["x"] = {"y": 2, "fix": -3}
    expected["python_dict"]["a"]["x"] = {"y": 2, "fix": -3}
    assert mock_persistent == expected
    assert parameters.python_dict["a"]["x"]["y"] == 2

    parameters.python_dict["a"]["x"]["y"] = 3
    expected["python_dict"]["a"]["x"]["y"] = 3
    assert mock_persistent == expected
    assert parameters.python_dict["a"]["x"]["y"] == 3


def test_persistent_ndarray(mock_bliss):
    python_arr = list()
    persistent_arr = PersistentNdArray("test")
    with pytest.raises(IndexError):
        persistent_arr[0]
    with pytest.raises(IndexError):
        persistent_arr[-1]
    numpy.testing.assert_array_equal(python_arr, persistent_arr[()])

    add = numpy.random.uniform(low=0, high=1, size=10)
    python_arr.append(add)
    persistent_arr.append(add)
    python_arr_copy = numpy.array(python_arr)
    numpy.testing.assert_array_equal(python_arr_copy[0], persistent_arr[0])
    numpy.testing.assert_array_equal(python_arr_copy[-1], persistent_arr[-1])
    numpy.testing.assert_array_equal(python_arr_copy, persistent_arr[()])

    add = numpy.random.uniform(low=0, high=1, size=(2, 10))
    python_arr.extend(add)
    persistent_arr.extend(add)
    python_arr_copy = numpy.array(python_arr)
    numpy.testing.assert_array_equal(python_arr_copy[0], persistent_arr[0])
    numpy.testing.assert_array_equal(python_arr_copy[-1], persistent_arr[-1])
    numpy.testing.assert_array_equal(python_arr_copy, persistent_arr[()])

    numpy.testing.assert_array_equal(python_arr_copy[2, 5:6], persistent_arr[2, 5:6])


def test_persistent_ordered_dict(mock_bliss):
    python_dict = dict()
    persistent_dict = PersistentOrderedDict("test")
    python_dict["string"] = "abc"
    persistent_dict["string"] = "abc"
    python_dict["number"] = 123
    persistent_dict["number"] = 123
    python_dict["list"] = [123, 456]
    persistent_dict["list"] = [123, 456]
    python_dict["dict"] = {"key": "value"}
    persistent_dict["dict"] = {"key": "value"}
    assert python_dict == persistent_dict.get_all()
