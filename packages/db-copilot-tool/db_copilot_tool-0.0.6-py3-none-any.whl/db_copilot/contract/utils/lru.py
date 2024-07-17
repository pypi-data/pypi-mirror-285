import time
from collections import OrderedDict

class LRUCacheDict(OrderedDict):
    """Dict with a limited length, ejecting LRUs as needed."""

    def __init__(self, *args, capacity: int = 10000, del_callback=None, **kwargs):
        assert capacity > 0
        self.capacity = capacity
        self.del_callback = del_callback
        self._access_times = {}
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        super().move_to_end(key)
        self._access_times[key] = time.time()

        while len(self) > self.capacity:
            old_key = next(iter(self))
            old_val = super().__getitem__(old_key)
            self.__delitem__(old_key)

            # callback to do something when an item is deleted
            if self.del_callback:
                self.del_callback(old_key, old_val)

    def __getitem__(self, key):
        val = super().__getitem__(key)
        super().move_to_end(key)
        self._access_times[key] = time.time()
        return val
    
    def __delitem__(self, key):  
        super().__delitem__(key)
        del self._access_times[key]

    def clear_cache(self, max_duration, callback=None):
        """
        Clear cache items that are older than max_duration
        """
        now = time.time()        
        for key, val in list(self.items()):
            access_time = self._access_times[key]
            if now - access_time > max_duration:
                self.__delitem__(key)                
                if callback:
                    callback(key, val)
                # callback to do something when an item is deleted
                if self.del_callback:
                    self.del_callback(key, val)                
            else:
                break