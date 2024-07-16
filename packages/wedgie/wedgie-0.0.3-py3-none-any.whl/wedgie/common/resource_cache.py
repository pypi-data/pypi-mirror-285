import time
import json
from random import choices
import string
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
import os
from functools import wraps
import threading
import atexit
from copy import deepcopy
from pathlib import Path

from logging import getLogger
import structlog

__logger = getLogger(__name__)
structlog.configure()
log = structlog.wrap_logger(__logger)


class ResourceCache:
    DEFAULT_CACHE_DIR = "/tmp"
    DEFAULT_TABLE_NAME = "cache"
    DEFAULT_WRITE_EXPIRY = 86400 * 7  # Store for a week, but don't actually use it unless it's newer than the read expiry
    DEFAULT_READ_EXPIRY = 3600  # By default, only 1h read expiry

    VERBOSE = False
    _store_nones = None
    read_expiry = None
    write_expiry = None

    def __init__(self, cache_file_name, cache_dir=None, table_name=None, read_expiry: int = None, write_expiry: int = None, store_nones=True, verbose: bool = None):
        self._parent_classes = []
        self._default_table_name = table_name or self.DEFAULT_TABLE_NAME

        self._file_name = cache_file_name
        self._cache_dir = cache_dir or self.DEFAULT_CACHE_DIR
        if not os.path.exists(self._cache_dir):
            raise FileNotFoundError(f"Cache directory does not exist: {self._cache_dir}")
        self._cache_dir = os.path.join(self._cache_dir, 'wedgie_custom_cache')

        # Ensure the directory exists by creating it if it doesn't
        __cache_path = Path(self._cache_dir)
        __cache_path.mkdir(parents=True, exist_ok=True)

        if os.path.dirname(cache_file_name):
            # If a full path was passed for the file name, just use that
            self._file_name = os.path.basename(cache_file_name)
            self._cache_dir = os.path.dirname(os.path.abspath(cache_file_name))

        self._cache_path = os.path.join(self._cache_dir, self._file_name)

        self.__log = self._make_logger()

        if not self._file_name:
            self.__log.fatal('Cache file name cannot be blank')
            raise ValueError('Cache file name cannot be blank')

        self._store_nones = store_nones
        self.read_expiry = read_expiry or self.DEFAULT_READ_EXPIRY
        self.write_expiry = write_expiry or self.DEFAULT_WRITE_EXPIRY
        if verbose is not None:
            self.VERBOSE = verbose is True

        self.__log.debug(f"Cache initializing",
                         cache_path=self._cache_path,
                         write_expiry=self.write_expiry,
                         read_expiry=self.read_expiry,
                         store_nones=store_nones,
                         verbose=self.VERBOSE)

        # CachingMiddleware.WRITE_CACHE_SIZE = 10_000
        self.db = TinyDB(self._cache_path, storage=CachingMiddleware(JSONStorage), indent=2)
        self.__log.info(f"Successfully initialized cache", file_path=self._cache_path)
        # ToDo eventually come back to this and expand to be able to use custom tables for stuff
        self.default_table = self.db.table(self._default_table_name)
        # I am probably overusing this, as it may not be needed for any read/get/search operations, but the couple
        # extra seconds it takes isn't hurting so far
        self.lock = threading.Lock()  # Threading lock for concurrency control
        _ = atexit.register(self.close)
        self.cache_eviction()

    def _make_logger(self, **kwargs):
        # make sure all loggers contain the key default fields
        kwargs.update(dict(name=self._file_name, table_name=self._default_table_name))
        return log.new(**kwargs)

    def is_open(self):
        return getattr(self.db, "_opened")

    def close(self):
        if self.is_open:
            self.cache_eviction()
            self.db.close()
            self.__log.info("Cache saved successfully", file_path=self._cache_path)

    def __log_verbose(self, msg, custom_logger=None, **kwargs):
        custom_logger = custom_logger or self.__log
        if self.VERBOSE:
            custom_logger.debug(msg, **kwargs)

    def add_self_classes(self, *args):
        """
        To use the cache decorator from within a class, we must be able to recognize what arbitrary arg inputs are a
        part of a parent class and should be ignored, otherwise they are seen as are unexpected inputs.
        """
        for a in args:
            if a not in self._parent_classes:
                self._parent_classes.append(a)

    def _generate_key(self, func, args, kwargs):
        # Workaround: if the cache decorator is used within a class, then it will pass an unexpected arg for "self."
        # By providing the class objects, we can recognize and remove those.
        copied_args = [a for a in args]
        while copied_args and isinstance(copied_args[0], tuple(self._parent_classes)):
            del copied_args[0]
        if isinstance(func, str):
            func_name = func
        else:
            func_name = func.__name__
        """Generate a unique key based on the function name and its arguments."""
        key_data = {
            'func_name': func_name,
            'args': copied_args,
            'kwargs': dict(sorted(kwargs.items()))
        }
        return json.dumps(key_data)

    @staticmethod
    def _get_age_from_result(cache_obj):
        if cache_obj is None:
            return
        current_time = time.time()
        return int(round(current_time - cache_obj['timestamp']))

    def get_cache(self, func, args, kwargs, read_expiry: int = None):
        """Retrieve the cached result if it exists and is not expired."""
        result = self.get_cache_raw(func=func, args=args, kwargs=kwargs, read_expiry=read_expiry)
        if result is None:
            return None, None
        return result['value'], self._get_age_from_result(result)

    def get_cache_raw(self, func, args, kwargs, read_expiry: int = None):
        """Retrieve the cached result if it exists and is not expired."""
        # split out to be able to call this way for test purposes
        key = self._generate_key(func, args, kwargs)
        return self.get_cache_manual(key=key, read_expiry=read_expiry)

    def get_cache_manual(self, key, read_expiry: int = None):
        if not isinstance(key, str):
            raise TypeError('Key must already be a string')
        with self.lock:  # Ensure that TinyDB access is thread-safe
            result = self.default_table.get(Query().key == key)
        if read_expiry is None:
            read_expiry = self.read_expiry

        if result is None:
            self.__log_verbose("No cached value found", key=key)
            return

        age = self._get_age_from_result(result)
        if read_expiry is not None:
            if age > read_expiry:
                # Cache expired
                self.__log_verbose("Cache found, but age not allowed", key=key, age=age)
                return

        self.__log_verbose("Valid cache found", key=key, age=age)
        return deepcopy(result)

    def get_all_cache_for_function(self, func):
        """Retrieve all cache values for a given function."""
        if isinstance(func, str):
            func_name = func
        else:
            func_name = func.__name__

        with self.lock:  # Ensure that TinyDB access is thread-safe
            result = self.default_table.search(Query().func_name == func_name)
        return result

    def delete_all_cache_for_function(self, func):
        """Retrieve all cache values for a given function."""
        if isinstance(func, str):
            func_name = func
        else:
            func_name = func.__name__

        with self.lock:  # Ensure that TinyDB access is thread-safe
            result = self.default_table.remove(Query().func_name == func_name)
        return result

    def set_cache(self, func, args, kwargs, value):
        """Cache the result of the function with a timestamp."""
        key = self._generate_key(func, args, kwargs)
        if value is None and not self._store_nones:
            self.__log.debug("Excluding None value from cache", key=key)
            return
        timestamp = time.time()
        self.__log_verbose("Storing resource cache", key=key, write_expiry=self.write_expiry)
        if isinstance(func, str):
            func_name = func
        else:
            func_name = func.__name__
        # Store func_name as its own field as well, even though it won't be used this way.
        #  This is so that I can easily find & purge all entries from a specific function if I want.
        with self.lock:  # Ensure that TinyDB access is thread-safe
            self.default_table.upsert({'func_name': func_name, 'key': key, 'value': deepcopy(value), 'timestamp': timestamp}, Query().key == key)

    def delete_cache(self, func, args, kwargs):
        key = self._generate_key(func, args, kwargs)
        self.__log.debug("Deleting resource cache", key=key)
        with self.lock:  # Ensure that TinyDB access is thread-safe
            self.default_table.remove(Query().key == key)

    def clear(self, table=None):
        if table:
            self.__log.warn(f"Dropping table from cache ({len(self.db.table(table).all())} rows)", table=table)
            self.db.drop_table(table)
            return

        tables = self.db.tables()
        if not tables:
            self.__log.warn("No tables to drop")
            return

        total_to_delete = 0
        for t in tables:
            total_to_delete += len(self.db.table(t).all())
        self.__log.warn(f"Resetting all cache data ({total_to_delete} total entries across {len(tables)} tables)")
        for t in tables:
            self.clear(t)

    def cache_eviction(self, table=None):
        def _cache_eviction(table_name=None):
            if table_name:
                __table_obj = self.db.table(table_name)
                deleted_entries = __table_obj.remove(Query().timestamp < time.time() - self.write_expiry)
                purged_ids.extend(deleted_entries)
                if deleted_entries:
                    self.__log.info(f"Eviction complete for table. Removed {len(deleted_entries)} expired entries.", table=table_name)
                else:
                    self.__log.debug(f"Eviction complete for table. Found no expired entries.", table=table_name)
                return
            self.__log.debug(f"Evicting old cache data from all tables")
            for t in self.db.tables():
                _cache_eviction(t)
        purged_ids = []
        _cache_eviction(table_name=table)
        if purged_ids:
            self.__log.info(f"Eviction complete. Removed a total of {len(purged_ids)} expired entries.", table=table)

    def cache(self, read_expiry=None):
        """Decorator to cache function results."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # generating random string to help correlate all log messages
                cache_call_id = ''.join(choices(string.ascii_uppercase + string.digits, k=8))
                __read_expiry = read_expiry if read_expiry is not None else self.read_expiry
                action_log = self._make_logger(cache_call_id=cache_call_id, read_expiry=__read_expiry)
                self.__log_verbose("Caching request received", custom_logger=action_log, key=self._generate_key(func, args, kwargs))

                if __read_expiry == 0:
                    action_log.debug(f"Skipping cache lookup; fetching resources from source")
                else:
                    cached_result, age = self.get_cache(func=func, args=args, kwargs=kwargs, read_expiry=__read_expiry)

                    if cached_result is None and not self._store_nones:
                        action_log.debug("Skipping None value; fetching resources from source")
                    elif age is not None:
                        action_log.debug(f"Returning result from cache")
                        return cached_result
                    else:
                        self.__log_verbose(f"No valid cache returned; fetching resources from source", custom_logger=action_log)

                result = func(*args, **kwargs)
                self.set_cache(func=func, args=args, kwargs=kwargs, value=result)
                return result
            return wrapper
        return decorator
