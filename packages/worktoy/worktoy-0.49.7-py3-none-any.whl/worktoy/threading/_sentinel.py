"""Sentinel enumerates sentinel values for the threads."""
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

import json
from typing import Optional

from worktoy.keenum import KeeNum, auto


class Sentinel(KeeNum):
  """Sentinel enumerates sentinel values for the threads."""

  NOOP = auto(0)
  PASS = auto(1)
  HALT = auto(2)
  EXIT = auto(3)
  KILL = auto(4)
  SYSEXIT = auto(5)

  @classmethod
  def unJava(cls, data: bytes, *_) -> Optional[Sentinel]:
    """Return the sentinel value from the JSON data."""
    dataJSON = data.decode('utf-8')
    dataDict = json.loads(dataJSON)
    name = dataDict.get('type_', )
    if name != 'Sentinel':
      return None
    args = [int(arg) for arg in dataDict.get('args', )]
    for item in cls:
      if item.value == args[0]:
        return item
    e = """Unable to parse sentinel"""
    raise ValueError(e)
