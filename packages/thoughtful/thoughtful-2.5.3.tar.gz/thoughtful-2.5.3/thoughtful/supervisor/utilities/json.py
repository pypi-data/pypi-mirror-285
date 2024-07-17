import json
import math


class JSONEncoder(json.JSONEncoder):
    """
    A JSON encoder that converts NaNs to None.
    """

    def iterencode(self, obj, _one_shot=False):
        return super().iterencode(self._nan_to_none(obj), _one_shot)

    def encode(self, obj, *args, **kwargs):
        return super().encode(self._nan_to_none(obj), *args, **kwargs)

    def _nan_to_none(self, obj):
        if isinstance(obj, dict):
            return {k: self._nan_to_none(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._nan_to_none(v) for v in obj]
        elif isinstance(obj, float) and math.isnan(obj):
            return None
        return obj
