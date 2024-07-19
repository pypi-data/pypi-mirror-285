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
from typing import Callable
from ruamel.yaml import YAML, CommentedMap
import sys
from re import Pattern

def dump_yaml(*args):
    yaml = YAML()
    for arg in args:
        if isinstance(arg, tuple):
            data, output = arg
            if output is None or output == "" or output == "-":
                yaml.dump(data, sys.stdout)
                return
            with open(output, 'w') as f:
                yaml.dump(data, f)
        else:
            yaml.dump(arg, sys.stdout)


def extract_regexp(items: dict, regexp: Pattern[str], d: CommentedMap, parent: str) -> list[dict[str, str]]:
  '''
  Extracts informations from CommentedMap on a regular expression pattern.

  Args:
    items (dict): The dictionary containing the comments to process
    regexp (Pattern[str]): The regular expression pattern used to match and extract information from comments.
    d (CommentedMap): The original CommentedMap object containing the comments and values.
    parent (str): The parent key used to construct the path of the extracted information.

  Returns:
    list[dict[str, str]]: A list of dictionaries containing the extracted information.

  '''
  ret = []
  for key, comments in items:
    # Match the comment with the regex and extract the operation and parameters
    if comments is None or len(comments) < 3 or comments[2] is None:
      continue
    groups = regexp.search(comments[2].value)
    if groups is not None and len(groups.groups()) > 1:
      retDict = {
        'path': parent + "." + key,
        'value': d[key]
      }
      retDict.update(groups.groupdict())
      retDict['params'] = retDict['params'].strip().split(
        ' ')  # split the parameters
      ret.append(retDict)
  return ret


def deep_visit(d: CommentedMap, parent: str, regexp: Pattern[str], extract_fun: Callable) -> list[dict[str, str]]:
  """
  Recursively visits a nested dictionary and extracts sub-dictionaries that contain a specific comment.

  Args:
    d (CommentedMap): The nested dictionary to be visited (as returned from ruamel.yaml)
    parent (str): The parent path of the current dictionary (default is an empty string).
    regexp (Pattern): The regular expression to be used to match the comment.
    extract_fun (Callable): The function used to extract the information from the comment. Must have the following signature:
      def extract_fun(items: dict, regexp: Pattern[str], d: CommentedMap, parent: str) -> list[dict[str, str]]:
        pass
  Returns:
    list[dict[str, str]]: A list of dictionaries containing the extracted information.
      Each dictionary contains the following keys:
      - 'path': The path of the current dictionary in the nested structure. eg: secure.admin.password
      - 'value': The value associated with the current nested structure.
      - The dictionary of any regexp match group found in the comment (if any)
  """

  def dv(d: CommentedMap, parent: str = "") -> list[dict[str, str]]:

    ret: list[dict] = []

    items = extract_fun(d.ca.items.items(), regexp, d, parent)
    if items is not None:
      ret = ret + items
    # Recursively visit sub-dictionaries and lists

    for k, v in d.items():
      if isinstance(v, dict):
        inner = dv(v, parent + "." + k)  # type: ignore
        if inner is not None and len(inner) > 0:
          ret = ret + inner
      elif isinstance(v, list):
        for i in v:
          if isinstance(i, dict):
            inner = dv(i, parent + "." + k)  # type: ignore
            if inner is not None and len(inner) > 0:
              ret = ret + inner
    return ret

  return dv(d, parent)
