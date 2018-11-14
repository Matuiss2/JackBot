from functools import wraps


def cache_forever(file):
    file.cache = {}

    @wraps(file)
    def inner(*args):
        if args not in file.cache:
            file.cache[args] = file(*args)
        return file.cache[args]

    return inner


def method_cache_forever(file):
    file.cache = {}

    @wraps(file)
    def inner(self, *args):
        if args not in file.cache:
            file.cache[args] = file(self, *args)
        return file.cache[args]

    return inner


def property_cache_forever(file):
    file.cached = None

    @wraps(file)
    def inner(self):
        if file.cached is None:
            file.cached = file(self)
        return file.cached

    return property(inner)
