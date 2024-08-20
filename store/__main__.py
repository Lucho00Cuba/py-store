# -*- encoding: UTF-8 -*-
"""
Provides a Python class that maps values to/from a JSON file
"""
from __future__ import absolute_import
import json
import os
import sys
from collections import OrderedDict
from copy import deepcopy

STRING_TYPES = (str,)
INT_TYPES = (int,)
if sys.version_info < (3,):
    STRING_TYPES += (unicode,)
    INT_TYPES += (long,)
VALUE_TYPES = (bool, int, float, type(None)) + INT_TYPES

class Store(object):
    """A class to provide object-based access to a JSON file"""

    def __init__(self, path: str, indent=2, auto_commit=True):
        if not isinstance(path, str):
            raise TypeError("The path must be a string.")
        self.__dict__.update(
            {
                "_auto_commit": auto_commit,
                "_data": None,
                "_path": path,
                "_indent": indent,
                "_states": [],
            }
        )
        try:
            self._load()
        except Exception as e:
            raise IOError(f"Failed to load the JSON file: {e}")

    def _load(self):
        """Load the JSON data from the file."""
        if not os.path.exists(self._path):
            try:
                with open(self._path, "w+b") as store:
                    store.write("{}".encode("utf-8"))
            except IOError as e:
                raise IOError(f"Failed to create the file: {e}")
        try:
            with open(self._path, "r+b") as store:
                raw_data = store.read().decode("utf-8")
        except IOError as e:
            raise IOError(f"Failed to read the file: {e}")
        
        if not raw_data:
            data = OrderedDict()
        else:
            try:
                data = json.loads(raw_data, object_pairs_hook=OrderedDict)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to decode JSON data: {e}")

        if not isinstance(data, dict):
            raise ValueError("Root element is not an object")
        
        self.__dict__["_data"] = data

    def _save(self):
        """Save the current state of the data to the file."""
        temp = self._path + "~"
        try:
            with open(temp, "wb") as store:
                output = json.dumps(self._data, indent=self._indent)
                store.write(output.encode("utf-8"))
        except IOError as e:
            raise IOError(f"Failed to write to the temporary file: {e}")

        try:
            if sys.version_info >= (3, 3):
                os.replace(temp, self._path)
            elif os.name == "windows":
                os.remove(self._path)
                os.rename(temp, self._path)
            else:
                os.rename(temp, self._path)
        except OSError as e:
            raise OSError(f"Failed to replace the original file: {e}")

    def _do_auto_commit(self):
        """Automatically save the data if auto-commit is enabled."""
        if self._auto_commit and not self.__dict__["_states"]:
            self._save()

    def __enter__(self):
        current_state = self.__dict__["_data"]
        self.__dict__["_states"].append(current_state)
        self.__dict__["_data"] = deepcopy(current_state)
        return self

    def __exit__(self, *args):
        previous_state = self.__dict__["_states"].pop()
        if any(args):
            self.__dict__["_data"] = previous_state
        elif not self.__dict__["_states"]:
            self._save()

    def __getattr__(self, key):
        if key in self._data:
            return deepcopy(self._data[key])
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{key}'")

    @classmethod
    def _verify_object(cls, obj, parents=None):
        """Raise an exception if the object is not suitable for assignment."""
        if isinstance(obj, (dict, list)):
            if parents is None:
                parents = []
            elif any(o is obj for o in parents):
                raise ValueError("Cycle detected in list/dictionary")
            parents.append(obj)

        if isinstance(obj, dict):
            for k, v in obj.items():
                if not cls._valid_string(k):
                    raise TypeError("A dict has non-string keys")
                cls._verify_object(v, parents)
        elif isinstance(obj, (list, tuple)):
            for o in obj:
                cls._verify_object(o, parents)
        else:
            return cls._valid_value(obj)

    @classmethod
    def _valid_value(cls, value):
        if isinstance(value, VALUE_TYPES):
            return True
        else:
            return cls._valid_string(value)

    @classmethod
    def _valid_string(cls, value):
        if isinstance(value, STRING_TYPES):
            return True
        else:
            return False

    @classmethod
    def _canonical_key(cls, key):
        """Convert a set/get/del key into the canonical form."""
        if cls._valid_string(key):
            return tuple(key.split("."))
        if isinstance(key, (tuple, list)):
            key = tuple(key)
            if not key:
                raise TypeError("Key must be a string or non-empty tuple/list")
            return key
        raise TypeError("Key must be a string or non-empty tuple/list")

    def __setattr__(self, attr, value):
        self._verify_object(value)
        self._data[attr] = deepcopy(value)
        self._do_auto_commit()

    def __delattr__(self, attr):
        try:
            del self._data[attr]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{attr}'")
        self._do_auto_commit()

    def __get_obj(self, steps):
        """Returns the object which is under the given path."""
        path = []
        obj = self._data
        for step in steps:
            if isinstance(obj, dict) and not self._valid_string(step):
                raise TypeError(f"{path} is a dict and {step} is not a string")
            try:
                obj = obj[step]
            except (KeyError, IndexError, TypeError) as e:
                raise type(e)(f"Unable to get {step} from {path}: {e}")
            path.append(step)
        return obj

    def __setitem__(self, key, value):
        steps = self._canonical_key(key)
        path, step = steps[:-1], steps[-1]

        # Create missing intermediate keys
        container = self._data
        for p in path:
            if p not in container or not isinstance(container[p], dict):
                container[p] = OrderedDict()
            container = container[p]

        self._verify_object(value)
        container[step] = deepcopy(value)
        self._do_auto_commit()

    def __getitem__(self, key):
        steps = self._canonical_key(key)
        obj = self.__get_obj(steps)
        return deepcopy(obj)

    def __delitem__(self, key):
        steps = self._canonical_key(key)
        path, step = steps[:-1], steps[-1]
        obj = self.__get_obj(path)
        try:
            del obj[step]
        except (KeyError, IndexError, TypeError) as e:
            raise type(e)(f"Unable to delete {step} from {path}: {e}")
        self._do_auto_commit()

    def __contains__(self, key):
        steps = self._canonical_key(key)
        try:
            self.__get_obj(steps)
            return True
        except (KeyError, IndexError, TypeError):
            return False