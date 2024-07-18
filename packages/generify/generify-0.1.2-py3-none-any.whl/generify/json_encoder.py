from json import JSONEncoder

import numpy as np
import pandas as pd


class GenerifyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            ret = tuple(obj)
        elif isinstance(obj, np.ndarray):
            ret = obj.tolist()
        elif isinstance(obj, np.dtype):
            if obj.names:
                ret = tuple((n, str(obj[n])) for n in obj)
            else:
                ret = str(obj)
        elif isinstance(obj, np.float128):
            ret = float(obj)
        elif isinstance(obj, pd.DataFrame):
            ret = obj.to_dict()
        else:
            ret = JSONEncoder.default(self, obj)

        return ret
