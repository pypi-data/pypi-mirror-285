def value_or_default(dict, k, default):
    """
    If k is in dict, returns its value. Otherwise, returns a default
    """
    if k in dict:
        return dict[k]
    return default


def value_or_none(dict, k):
    """
    If k is in dict, returns its value. Otherwise, returns None
    """
    value_or_default(dict, k, None)