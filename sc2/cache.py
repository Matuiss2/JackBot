"""Group all caches methods and properties"""
from functools import wraps


def cache_forever(file):
    """Cache anything forever"""
    file.cache = {}

    @wraps(file)
    def inner(*args):
        if args not in file.cache:
            file.cache[args] = file(*args)
        return file.cache[args]

    return inner


def method_cache_forever(file):
    """Cache anything forever(method)"""
    file.cache = {}

    @wraps(file)
    def inner(self, *args):
        if args not in file.cache:
            file.cache[args] = file(self, *args)
        return file.cache[args]

    return inner


def property_cache_forever(file):
    """Cache anything forever(property)"""
    file.cached = None

    @wraps(file)
    def inner(self):
        if file.cached is None:
            file.cached = file(self)
        return file.cached

    return property(inner)


def method_cache_once_per_frame(f):
    """ Untested but should work for functions with arguments
        Only works on properties of the bot object because it requires access to self.state.game_loop """
    f.frame = -1
    f.cache = {}

    @wraps(f)
    def inner(self, *args):
        if f.frame != self.state.game_loop:
            f.frame = self.state.game_loop
            f.cache = {}
        if args not in f.cache:
            f.cache[args] = f(self, *args)
        return f.cache[args]

    return inner


def property_cache_once_per_frame(f):
    """ This decorator caches the return value for one game loop,
     then clears it if it is accessed in a different game loop
    Only works on properties of the bot object because it requires access to self.state.game_loop """
    f.frame = -1
    f.cache = None

    @wraps(f)
    def inner(self):
        if f.frame != self.state.game_loop:
            f.frame = self.state.game_loop
            f.cache = None
        if f.cache is None:
            f.cache = f(self)
        return f.cache

    return property(inner)
