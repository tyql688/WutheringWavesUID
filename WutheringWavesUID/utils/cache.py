import time
from collections import OrderedDict


class TimedCache:
    def __init__(self, timeout=5, maxsize=10):
        self.cache = OrderedDict()
        self.timeout = timeout
        self.maxsize = maxsize

    def set(self, key, value):
        if len(self.cache) >= self.maxsize:
            self._clean_up()
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            self._clean_up()
        self.cache[key] = (value, time.time() + self.timeout)

    def get(self, key):
        if key in self.cache:
            value, expiry = self.cache.pop(key)
            if time.time() < expiry:
                self.cache[key] = (value, expiry)
                return value
        return None

    def delete(self, key):
        if key in self.cache:
            del self.cache[key]

    def _clean_up(self):
        current_time = time.time()
        while self.cache and self.cache[next(reversed(self.cache))][1][1] <= current_time:
            self.cache.popitem(last=False)
