from collections.abc import Iterable
import copy
from enum import Enum
from typing import Hashable
from argparse import Namespace

import numpy as np
import pandas as pd


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


def generify(obj, path=[], log=None, ids=None):
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
                kk = generify(k, path + [f"key->{k}"], log=log, ids=ids)
                v = obj[k]
                if callable(v):
                    continue
                ret_val = generify(v, path + [k], log=log, ids=ids)
                ret[kk] = ret_val
        elif isinstance(obj, list):
            is_rec = True
            for i in range(len(obj)):
                obj[i] = generify(obj[i], path + [i], log=log, ids=ids)
            ret = obj
        elif (
            isinstance(obj, tuple) and hasattr(obj, "_asdict") and hasattr(obj, "_fields")
        ):  # checking if it is a namedtuple
            is_rec = True
            ret = [None] * len(obj)
            for i in range(len(obj)):
                ret[i] = generify(obj[i], path + [i], log=log, ids=ids)
            ret = obj.__class__(*ret)
        elif isinstance(obj, tuple):
            is_rec = True
            ret = [None] * len(obj)
            for i in range(len(obj)):
                ret[i] = generify(obj[i], path + [i], log=log, ids=ids)
            ret = tuple(ret)
        elif isinstance(obj, set):
            ret = set()
            l = len(obj)
            for i in range(l):
                k = obj.pop()
                k = generify(k, path + [i], log=log, ids=ids)
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
        elif hasattr(obj, "__class__"):  # custom class, turn it into a dict
            is_rec = True
            keys = [k for k in dir(obj) if not (k.startswith("__") and k.endswith("__"))]
            ret = dict()
            for k in keys:
                kk = generify(k, path + [f"key->{k}"], log=log, ids=ids)
                v = getattr(obj, k)
                if callable(v):
                    continue
                ret_val = generify(v, path + [k], log=log, ids=ids)
                ret[kk] = ret_val
        else:
            unsupported = True
    except Exception as ex:
        # raise ex
        ret = f"Failed generify, Exception: {ex}"

    if unsupported:
        raise RuntimeError(f"Unsupported type '{type(obj)}', path: {path}.")

    if not is_rec and log:
        log(f"generify {path}: {ret}")

    # protect against circular dependency
    ids.remove(oid)

    return ret
