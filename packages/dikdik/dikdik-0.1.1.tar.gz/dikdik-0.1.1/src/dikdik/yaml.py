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


def deep_visit(d: CommentedMap, regexp: Pattern, parent: str) -> list[dict[str, str]]:
  """
  Recursively visits a nested dictionary and extracts sub-dictionaries that contain a specific comment.

  Args:
    d (CommentedMap): The nested dictionary to be visited (as returned from ruamel.yaml)
    regexp (Pattern): The regular expression to be used to match the comment.
    parent (str): The parent path of the current dictionary (default is an empty string).

  Returns:
    list[dict[str, str]]: A list of dictionaries containing the extracted information.
      Each dictionary contains the following keys:
      - 'path': The path of the current dictionary in the nested structure. eg: secure.admin.password
      - 'value': The value associated with the current nested structure.
      - The dictionary of any regexp match group found in the comment (if any)
  """

  ret: list[dict] = []
  for key, comments in d.ca.items.items():

    # Match the comment with the regex and extract the operation and parameters
    match = regexp.search(comments[2].value)
    if match is not None and len(match.groups()) > 1:

      matchDict = match.groupdict()

      ret.append(
          {'path': parent + "." + key,
           "value": d[key]}.update(matchDict)
           )

  # Recursively visit sub-dictionaries and lists

  for k, v in d.items():
    if isinstance(v, dict):
      ret = ret + deep_visit(v, regexp, parent + "." + k)  # type: ignore
    elif isinstance(v, list):
      for i in v:
        if isinstance(i, dict):
          ret = ret + deep_visit(i, regexp, parent + "." + k)  # type: ignore
  return ret
