#!/usr/bin/env python
#
# This file is part of dik-dik (https://github.com/mbovo/dikdik).
# Copyright (c) 2020-2023 Manuel Bovo.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import yaml
import json
import os

from io import TextIOWrapper
from typing import Any, Union, Tuple
from jsonschema import ValidationError, validate

class PowerDict():
    '''
      Powerdict is an advanced dict class
    '''

    def __init__(self, d: dict = {}, **kwargs):
        self._data = {}
        self._data.update(d)
        if kwargs:
            self._data.update(**kwargs)

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, key: str) -> Any:
        if key in self._data:
            return self._data[key]
        raise KeyError(key)

    def __setitem__(self, key, item):
        self._data[key] = item

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __repr__(self) -> str:
        return repr(self._data)

    def __str__(self) -> str:
        return str(self._data)

    def __copy__(self):
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        # Create a copy and avoid triggering descriptors
        inst.__dict__["data"] = self.__dict__["data"].copy()
        return inst

    def copy(self):
        if self.__class__ is PowerDict:
            return PowerDict(self._data.copy())
        import copy
        data = self._data
        try:
            self._data = {}
            c = copy.copy(self)
        finally:
            self._data = data
        c.update(self)
        return c

    def items(self):
        return self._data.items()

    def pop(self, key, default=None):
        return self._data.pop(key, default)

    def popitem(self):
        return self._data.popitem()

    def clear(self):
        self._data.clear()

    def get(self, key, default=None):
        return self._data.get(key, default)

    def setdefault(self, key, default=None):
        return self._data.setdefault(key, default)

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def update(self, *args, **kwargs):
        if args:
            if len(args) > 1:
                raise TypeError(
                    "update expected at most 1 arguments, got %d" % len(args))
            other = args[0]  # type: ignore
            if isinstance(other, PowerDict):
                other = other.data  # type: ignore
            elif not isinstance(other, dict):
                other = dict(other)
            self._data.update(other)
        for key, value in kwargs.items():
            self._data[key] = value

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def validate(self, schema: dict, raise_exception: bool = False) -> Union[None, Tuple[bool, str]]:
        if not raise_exception:
            try:
                validate(self._data, schema)
                return True, ""
            except ValidationError as e:
                return False, e.message
        else:
            validate(self._data, schema)

    def to_yaml(self, file_or_path: Union[str, TextIOWrapper]):
        if isinstance(file_or_path, str):
            with open(file_or_path, 'w') as file:
                yaml.safe_dump(self._data, file)
        else:
            yaml.safe_dump(self._data, file_or_path)

    def from_yaml(self, file_or_path: Union[str, TextIOWrapper], merge: bool = False):
        new_data = {}
        if isinstance(file_or_path, str):
            with open(file_or_path, 'r') as file:
                new_data = yaml.safe_load(file.read())
        else:
            new_data = yaml.safe_load(file_or_path.read())

        if merge:
            new_data = deep_merge(self._data, new_data)
        self.update(new_data)

    def to_json(self, file_or_path: Union[str, TextIOWrapper, None] = None) -> Union[None, str]:
        if file_or_path is None:
            return json.dumps(self._data, indent=2)
        if isinstance(file_or_path, str):
            with open(file_or_path, 'w') as file:
                json.dump(self._data, file)
        else:
            json.dump(self._data, file_or_path)

    def from_json(self, file_or_path: Union[str, TextIOWrapper], merge: bool = False):
        new_data = {}
        if isinstance(file_or_path, str):
            with open(file_or_path, 'r') as file:
                new_data = json.load(file)
        else:
            new_data = json.load(file_or_path)

        if merge:
            new_data = deep_merge(self._data, new_data)
        self.update(new_data)

    def from_env(self, prefix: str = ''):
        for key, value in os.environ.items():
            if key.startswith(prefix):
                self._data[key] = value


def deep_merge(d1:dict, d2:dict)-> dict:
    """
    Merges two dictionaries recursively.
    """
    merged = d1.copy()
    for k, v in d2.items():
        if isinstance(v, dict) and k in merged and isinstance(merged[k], dict):
            merged[k] = deep_merge(merged[k], v)
        elif isinstance(v, list) and k in merged and isinstance(merged[k], list):
            merged[k].extend(v)
        else:
            merged[k] = v
    return merged


def set_nested(d: dict, keys: list[str], value: str) -> None:
  """
  Sets a nested value in a dictionary based on a list of keys.

  Args:
    d (dict): The dictionary to modify.
    keys (list[str]): A list of keys representing the nested structure.
    value (str): The value to set.

  Returns:
    None
  """
  for key in keys[:-1]:
    d = d.setdefault(key, {})
  if keys[-1] is not None:
    d[keys[-1]] = value


def get_nested(d: dict, keys: list[str]) -> Any:
  """
  Gets a nested value in a dictionary based on a list of keys.

  Args:
    d (dict): The dictionary to search.
    keys (list[str]): A list of keys representing the nested structure.

  Returns:
    Any: The value found in the nested structure.
  """
  p = d.copy()
  for key in keys:
    p = p[key]
  return p
