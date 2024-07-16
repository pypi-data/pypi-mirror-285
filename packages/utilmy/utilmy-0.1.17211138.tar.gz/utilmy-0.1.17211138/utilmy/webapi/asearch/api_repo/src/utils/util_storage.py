from typing import Dict

import diskcache
import fire

from src.utils.util_log import log, loge


#######################################################################################
def storage_init(cfg: dict):
    return Storage(cfg)


class DictStorage:
    def __init__(self):
        """Initialize Storage object with an empty dictionary as 'store' attribute."""
        self.store = {}

    def get(self, key: str, default=None):
        return self.store.get(key, default)

    def put(self, key: str, value):
        return self.store.update({key: value})


class DiskcacheStorage:
    def __init__(self, cache_path="/tmp/diskcache/", cache_max_size=1e9, ttl=3600):
        """Initializes a new instance of diskcache : multithreading, persistent.
           Max size of cache on disk.
           After ttl time, data will be removed from disk.

        Args:
            cache_path (str): path to cache directory.
            cache_max_size (float, optional): maximum size of cache in bytes. Defaults to 1e9.

        Returns:
            None
        """
        self.store = diskcache.Cache(directory=cache_path, size_limit=cache_max_size)
        self.ttl = ttl

    def get(
        self,
        key: str,
    ):
        try:
            ddict: dict = self.store.get(key)
            return ddict

        except Exception as e:
            loge(e)
            return None

    def put(self, key: str, value):
        try:
            self.store.set(key, value, expire=self.ttl)
        except Exception as e:
            loge(e)


class Storage:
    def __init__(self, cfg: dict):
        """Initializes Storage object with given configuration.
        Args:
            cfg (dict): configuration dictionary.

        Returns:
            None

        TODO:
            - Implement Redis acces.
            - Implement other persistent storage.
            - Implement Error handling for storage.
            - Handle better default values.

        """
        name = cfg.get("service", {}).get("storage_name", "diskcache")

        if name == "diskcache":
            cfgdb = cfg.get("diskcache", {"cache_path": "/tmp/diskcache/", "cache_max_size": 1e9})
            self.store = DiskcacheStorage(cfgdb["cache_path"], cfgdb["cache_max_size"])
            return None
        else:
            raise Exception(f"Not implemented {name} storage")

    def get(
        self,
        key: str,
    ) -> Dict:
        djson: dict = self.store.get(key)
        return djson

    def put(self, key: str, value):
        return self.store.put(key, value)

    def close(
        self,
    ):
        log("closing DB")
        return True


####################################################################################
if __name__ == "__main__":
    fire.Fire()
