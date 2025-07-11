def deep_get(dictionary, keys, default=None):
    """递归获取字典深层的值"""
    for key in keys:
        if dictionary is None:
            return default
        dictionary = dictionary.get(key)
    return dictionary or default