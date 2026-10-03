from collections.abc import Mapping


def deep_get(dictionary, keys, default=None):
    """递归获取字典深层的值"""
    for key in keys:
        if not isinstance(dictionary, Mapping):
            return default
        dictionary = dictionary.get(key)
    return default if dictionary is None else dictionary
