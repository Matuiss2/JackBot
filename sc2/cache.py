from collections import Counter
from functools import wraps
import numpy as np


def property_cache_forever(func):
    @wraps(func)
    def inner(self):
        property_cache = "_cache_" + func.__name__
        cache_updated = hasattr(self, property_cache)
        if not cache_updated:
            setattr(self, property_cache, func(self))
        cache = getattr(self, property_cache)
        return cache

    return property(inner)


def property_cache_once_per_frame(func):
    """ This decorator caches the return value for one game loop,
    then clears it if it is accessed in a different game loop.
    Only works on properties of the bot object, because it requires
    access to self.state.game_loop """

    @wraps(func)
    def inner(self):
        property_cache = "_cache_" + func.__name__
        state_cache = "_frame_" + func.__name__
        cache_updated = hasattr(self, property_cache) and getattr(self, state_cache, None) == self.state.game_loop
        if not cache_updated:
            setattr(self, property_cache, func(self))
            setattr(self, state_cache, self.state.game_loop)

        cache = getattr(self, property_cache)
        should_copy = type(cache).__name__ == "Units" or isinstance(cache, (list, set, dict, Counter, np.ndarray))
        if should_copy:
            return cache.copy()
        return cache

    return property(inner)


def property_immutable_cache(func):
    """ This cache should only be used on properties that return an immutable object """

    @wraps(func)
    def inner(self):
        if func.__name__ not in self.cache:
            self.cache[func.__name__] = func(self)
        return self.cache[func.__name__]

    return property(inner)


def property_mutable_cache(func):
    """ This cache should only be used on properties that return a mutable object (Units, list, set, dict, Counter) """

    @wraps(func)
    def inner(self):
        if func.__name__ not in self.cache:
            self.cache[func.__name__] = func(self)
        return self.cache[func.__name__].copy()

    return property(inner)
