"""MinecraftEvent enumerates discrete minecraft events using the KeeNum
class. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

import json
from typing import Optional, TypeAlias, Self

from worktoy.keenum import KeeNum, auto

Event: TypeAlias = Optional[Self]


class MinecraftEvent(KeeNum):
  """MinecraftEvent enumerates discrete minecraft events using the KeeNum
  class. """

  CLIENT_START = auto(0)
  CLIENT_CLOSE = auto(1)
  WORLD_LOADED = auto(2)
  WORLD_CLOSED = auto(3)

  @classmethod
  def unJava(cls, data: bytes, *_) -> Event:
    """Return the minecraft event from the JSON data."""
    dataJSON = data.decode('utf-8')
    dataDict = json.loads(dataJSON)
    name = dataDict.get('type_', )
    if name != 'MinecraftEvent':
      return None
    args = [int(arg) for arg in dataDict.get('args', )]
    for item in cls:
      if item.value == args[0]:
        return item
    e = """Unable to parse minecraft event"""
    raise ValueError(e)
