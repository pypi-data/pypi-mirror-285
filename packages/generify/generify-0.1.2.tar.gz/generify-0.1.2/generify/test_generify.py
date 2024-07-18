from collections import namedtuple
from enum import Enum
import pickle
import pytest
import json


from generify import generify, GenerifyJSONEncoder, GenerifyException, GenerifyGetAttrException
from generify.convert import TestException

import numpy as np
import pandas as pd


class EnumA(Enum):
    A1 = "a1_val"
    B1 = 3


GEN_A1 = ("A1", "a1_val")

NamedT = namedtuple("NamedT", "aa bb cc")
N1 = NamedT(1, 2, EnumA.A1)
GEN_N1 = NamedT(1, 2, GEN_A1)


class Scalar:
    def __init__(self) -> None:
        self.val_int = 3
        self.val_float = 10.0
        self.val_str = "jhon"
        self.val_bool = True
        self.val_enum = EnumA.A1
        self.val_np_scalar = np.float128(30)
        self.val_dtype = np.dtype("float")

    def __eq__(self, other: dict):
        return (
            len(other) == 7
            and self.val_int == other["val_int"]
            and self.val_float == other["val_float"]
            and self.val_str == other["val_str"]
            and self.val_bool == other["val_bool"]
            and GEN_A1 == other["val_enum"]
            and self.val_np_scalar == other["val_np_scalar"]
            and other["val_np_scalar"].dtype == np.float128
            and self.val_dtype == other["val_dtype"]
            and self.val_bool == other["val_bool"]
        )


class Nested:
    def __init__(self) -> None:
        self.a = 3
        self.scalar = Scalar()

    def __eq__(self, other: dict):
        return self.a == other["a"] and self.scalar == other["scalar"]


class Mix:
    def __init__(self) -> None:
        self.val = {
            "v1": [1, Nested()],
            "v2": [1, "2", True],
            "v_np1": np.array([1, 2, 3]),
            "v_df1": pd.DataFrame({"col1": [1, 2, 3], "col2": [10, 20, 30]}),
            "v_sc": Scalar(),
            "v_mix1": [5, Scalar(), set([2, "a"])],
        }


def assert_dict_a(ret):
    assert ret[1] == 3
    assert ret["2"] == 4
    assert ret[(1, 2)] == 10


# self.val_nested = [[1, 2], Scalar(), [1, 2, 3], [[5, Scalar(), 7], [2]]]


def test_scalar():
    ret = generify(Scalar())
    assert ret == Scalar()


def test_enum():
    ret = generify(EnumA.A1)
    assert ret == GEN_A1


def test_list():
    ret = generify([1, 2, 3])
    assert ret == [1, 2, 3]

    val = [1, Scalar(), 10.3, {1: 3, "2": 4, (1, 2): 10}]
    ret = generify(val)
    assert ret == [*val]


def test_tuples():
    ret = generify((1, 2, 3))
    assert ret == (1, 2, 3)

    val = (1, Scalar(), 10.3, {1: Scalar(), "2": 4, (1, 2): 10})
    ret = generify(val)
    assert ret == tuple([*val])


def test_sets():
    ret = generify(set([1, 2, 3]))
    assert ret == set([1, 2, 3])

    val = [1, 10.3, (1, "2", True)]
    ret = generify(set(val))
    assert ret == set([*val])


def test_namedtuple():
    val_named = NamedT(0.5, (1, 2), Scalar())

    ret = generify(val_named)
    assert ret == val_named
    assert isinstance(ret.cc, dict)

    assert generify(N1) == GEN_N1


def test_dictionary():
    ret = generify(
        {
            "a": 2,
            "b": [1, 20.2, "dan", Scalar()],
            1: 500,
            EnumA.A1: 30,
            N1: "hi",
        }
    )
    assert ret == {
        "a": 2,
        "b": [1, 20.2, "dan", Scalar()],
        1: 500,
        GEN_A1: 30,
        GEN_N1: "hi",
    }


def test_numpy_arr():
    ret = generify(np.array([1, 2, 3]))
    assert np.array_equal(ret, [1, 2, 3])
    assert isinstance(ret, np.ndarray)

    ret = generify(np.array([[1, 2, 3], [4, 5, 6]]))
    assert np.array_equal(ret, [[1, 2, 3], [4, 5, 6]])
    assert isinstance(ret, np.ndarray)


def test_dataframe():
    val = pd.DataFrame({"col1": [1, 2, 3], "col2": [10, 20, "30"]})
    ret = generify(val)
    assert pd.DataFrame.equals(val, ret)
    assert isinstance(ret, pd.DataFrame)


def test_nested_object():
    ret = generify(Nested())
    assert ret == Nested()


def test_circular_references():
    # circular references - objects which points to self
    ref = {"x": 3}
    ref["ref"] = ref
    ret = generify(ref)
    assert ret["x"] == 3
    assert ret["ref"] == f"oid-{id(ref)}"


def test_raise_exception():
    # no exception
    ret = generify(TestException(), raise_exception=False)
    assert ret == "Failed generify, Exception: test exception"

    # exception
    with pytest.raises((GenerifyException)) as excinfo:
        generify({"a": [0, TestException()]}, raise_exception=True)
    assert "Failed generify ['a', 1]" == str(excinfo.value)


class GetAttrTest:
    @property
    def test(self):
        raise Exception("test exception")


def test_raise_getattr_exception():
    # no exception
    ret = generify(GetAttrTest(), raise_getattr_exception=False)
    assert ret["test"] == "Failed getattr, Exception: test exception"

    # exception
    with pytest.raises((GenerifyGetAttrException)) as excinfo:
        generify({"a": GetAttrTest()}, raise_getattr_exception=True)
    assert "Failed getattr ['a', 'test']" == str(excinfo.value)


def test_mix():
    ret = generify(Mix())
    assert len(ret) == 1
    assert ret["val"]["v1"] == [1, Nested()]
    assert ret["val"]["v2"] == [1, "2", True]
    assert np.array_equal(ret["val"]["v_np1"], np.array([1, 2, 3]))
    assert pd.DataFrame.equals(ret["val"]["v_df1"], pd.DataFrame({"col1": [1, 2, 3], "col2": [10, 20, 30]}))
    assert ret["val"]["v_sc"] == Scalar()
    assert ret["val"]["v_mix1"] == [5, Scalar(), set(["a", 2])]


def test_mix_pickle():
    mix = generify(Mix())
    try:
        bytes = pickle.dumps(mix)
        pickle.loads(bytes)
    except Exception as ex:
        pytest.fail(f"failed pickle mix. [{ex.__class.__name__}]: {ex}")


def test_mix_json():
    mix = generify(Mix())
    try:
        jtext = json.dumps(mix, cls=GenerifyJSONEncoder)
        json.loads(jtext)
    except Exception as ex:
        pytest.fail(f"failed pickle mix. [{ex.__class__.__name__}]: {ex}")


if __name__ == "__main__":
    ret = generify(
        NamedT(1, 2, 3),
        # EnumA.A1,
        log=print,
    )
    print(ret)
