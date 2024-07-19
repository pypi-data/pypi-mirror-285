import functools

__all__ = ["lru_cache", "cache"]


class _HDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))


class _HSet(set):
    def __hash__(self):
        return hash(frozenset(self))


class _HList(list):
    def __hash__(self):
        return hash(tuple(self))


def _hashable(func):
    def convert(obj):
        if isinstance(obj, dict):
            return _HDict({k: convert(v) for k, v in obj.items()})
        if isinstance(obj, list):
            return _HList([convert(o) for o in obj])
        if isinstance(obj, set):
            return _HSet([convert(o) for o in obj])
        return obj

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        args = tuple([convert(arg) for arg in args])
        kwargs = {k: convert(v) for k, v in kwargs.items()}
        return func(*args, **kwargs)

    return wrapped


def lru_cache(maxsize=128, typed=False):
    def decorator(func):
        return functools.lru_cache(maxsize=maxsize, typed=typed)(_hashable(func))

    return decorator


def cache():
    return lru_cache(maxsize=None, typed=False)
