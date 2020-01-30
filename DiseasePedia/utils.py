import functools


def transform_to(trans):
    """Ensuring Return List"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return trans(func(*args, **kwargs))

        return wrapper

    return decorator


def map_key(keys, func):
    if not isinstance(keys, list):
        return map_key([keys], func)
    return transform_to(lambda obj: dict(obj, **{key: func(obj.get(key)) for key in keys}))


def apply_func_to_keys(keys, func):
    return lambda obj: dict(obj, **{key: func(obj.get(key)) for key in keys if key in obj})


def map_list(f):
    return transform_to(lambda xs: list(map(f, xs)))


def extracted(func):
    return lambda args: func(*args)
