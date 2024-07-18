from collections.abc import Iterable
from enum import Enum

import numpy as np
import pandas as pd


class TestException:
    pass


class GenerifyException(Exception):
    pass


class GenerifyGetAttrException(Exception):
    pass


def df_handler(df, path, log):
    is_simple_df = True
    for type in df.dtypes.tolist():
        if not np.issctype(type):
            is_simple_df = False
            break
    if is_simple_df:
        return df
    else:
        df_ret = df.copy()
        for column in df_ret.columns:
            if np.issctype(df_ret[column].dtypes):
                if log:
                    log(f"generify {path + [column]}: {df_ret[column].dtypes}")
                continue
            row_list = []
            for i, row in enumerate(df_ret.index):
                res = generify(df_ret[column][row], path + [column, i], log=log)
                row_list.append(res)
            df_ret[column] = row_list
        return df_ret


def generify(obj, path=[], log=None, ids=None, raise_exception=False, raise_getattr_exception=False):
    def _generify(obj, path):
        return generify(
            obj,
            path,
            log=log,
            ids=ids,
            raise_exception=raise_exception,
            raise_getattr_exception=raise_getattr_exception,
        )

    unsupported = False
    is_rec = False

    if ids is None:
        ids = set()

    # protect against circular dependency
    oid = id(obj)
    if oid in ids:
        return f"oid-{oid}"
    ids.add(oid)

    # handle obj type
    try:
        if obj is None:
            ret = obj
        elif isinstance(obj, pd.DataFrame):
            ret = df_handler(obj, path, log=log)
        elif isinstance(obj, dict):
            is_rec = True
            ret = dict()
            for k in obj.keys():
                kk = _generify(k, path + [f"key->{k}"])
                v = obj[k]
                if callable(v):
                    continue
                ret_val = _generify(v, path + [k])
                ret[kk] = ret_val
        elif isinstance(obj, list):
            is_rec = True
            ret = [None] * len(obj)
            for i in range(len(obj)):
                ret[i] = _generify(obj[i], path + [i])
        elif (
            isinstance(obj, tuple) and hasattr(obj, "_asdict") and hasattr(obj, "_fields")
        ):  # checking if it is a namedtuple
            is_rec = True
            ret = [None] * len(obj)
            for i in range(len(obj)):
                ret[i] = _generify(obj[i], path + [i])
            ret = obj.__class__(*ret)
        elif isinstance(obj, tuple):
            is_rec = True
            ret = [None] * len(obj)
            for i in range(len(obj)):
                ret[i] = _generify(obj[i], path + [i])
            ret = tuple(ret)
        elif isinstance(obj, set):
            is_rec = True
            ret = set()
            l = len(obj)
            for i in range(l):
                k = obj.pop()
                k = _generify(k, path + [i])
                ret.add(k)
            pass
        elif isinstance(obj, np.dtype):
            ret = obj
        elif isinstance(obj, np.ndarray):
            if obj.dtype.kind == "O":
                raise RuntimeError(f"Unsupported numpy array, dtype=object, path: {path}.")
            ret = obj
        elif np.isscalar(obj):
            ret = obj
        elif isinstance(obj, Enum):
            # enum is converted to hashable type tuple
            ret = (obj.name, obj.value)
        elif isinstance(obj, Iterable):
            is_rec = True
            ret = generify(list(obj), path, log=log, ids=ids)
        elif isinstance(obj, TestException):
            raise Exception("test exception")
        elif hasattr(obj, "__class__"):  # custom class, turn it into a dict
            is_rec = True
            keys = [k for k in dir(obj) if not (k.startswith("__") and k.endswith("__"))]
            ret = dict()
            for k in keys:
                kk = _generify(k, path + [f"key->{k}"])
                try:
                    v = getattr(obj, k)
                except Exception as ex:
                    if raise_getattr_exception:
                        raise GenerifyGetAttrException(f"Failed getattr {path + [k]}") from ex
                    v = f"Failed getattr, {ex.__class__.__name__}: {ex}"
                if callable(v):
                    continue
                ret_val = _generify(v, path + [k])
                ret[kk] = ret_val
        else:
            unsupported = True
    except Exception as ex:
        # if getattr exception was raise keep perculating it
        if isinstance(ex, GenerifyGetAttrException):
            raise ex

        if raise_exception:
            # recursive exception catch
            if isinstance(ex, GenerifyException):
                raise ex
            raise GenerifyException(f"Failed generify {path}") from ex
        ret = f"Failed generify, {ex.__class__.__name__}: {ex}"

    if unsupported:
        raise RuntimeError(f"Unsupported type '{type(obj)}', path: {path}.")

    if not is_rec and log:
        log(f"generify {path}: {ret}")

    # protect against circular dependency
    ids.remove(oid)

    return ret
