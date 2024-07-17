import threading
import time


class MemoryCache:
    def __init__(self, expiry_time):
        self.cache = {}
        self.expiry_time = expiry_time
        self.timer = threading.Timer(expiry_time, self.delete_expired_items)
        self.timer.start()

    def get(self, key, default=None, refresh_expiry=True):
        if key in self.cache and time.time() - self.cache[key][1] < self.expiry_time:
            if refresh_expiry:
                self.cache[key] = (self.cache[key][0], time.time())
            return self.cache[key][0]
        else:
            return default

    def get_all(self):
        return {key: value[0] for key, value in self.cache.items()}

    def set(self, key, value):
        self.cache[key] = (value, time.time())

    def delete_expired_items(self):
        now = time.time()
        for key, (_, timestamp) in self.cache.items():
            if now - timestamp >= self.expiry_time:
                del self.cache[key]
        self.timer = threading.Timer(self.expiry_time, self.delete_expired_items)
        self.timer.start()

    def delete(self):
        del self.cache
        self.timer.cancel()
