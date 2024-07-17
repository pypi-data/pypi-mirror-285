"""Player encapsulates the python reflection of the java player object.
Please note that the java player object contains a pile of obfuscated
fields and other cringe. This class exposes the most fundamental fields.
Please note that this class is not intended to transmit data to the java
instance of minecraft. It merely exposes player related data. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

import json
from typing import Optional, TYPE_CHECKING

from worktoy.desc import AttriBox
from worktoy.ezdata import EZData, BeginFields, EndFields

if TYPE_CHECKING:
  from worktoy.mineside import FromJava


class Player(EZData):
  """Player encapsulates the python reflection of the java player object.
  Please note that the java player object contains a pile of obfuscated
  fields and other cringe. This class exposes the most fundamental fields.
  Please note that this class is not intended to transmit data to the java
  instance of minecraft. It merely exposes player related data. """

  BeginFields
  xf = AttriBox[float](0.0)
  yf = AttriBox[float](0.0)
  zf = AttriBox[float](0.0)
  yaw = AttriBox[float](0.0)
  pitch = AttriBox[float](0.0)
  timeStamp = AttriBox[float](0.0)  # the time since epoch
  timeDelta = AttriBox[float](-1.0)  # diff between last update and now
  EndFields

  def update(self, *args, **kwargs) -> None:
    """Update the player with the new data."""
    self.xf = kwargs['xf']
    self.yf = kwargs['yf']
    self.zf = kwargs['zf']
    self.yaw = kwargs['yaw']
    self.pitch = kwargs['pitch']

  @classmethod
  def unJava(cls, data: bytes, fromJava: FromJava) -> Optional[Player]:
    """Converts a byte object from Java to a Python object."""
    dataJSON = data.decode('utf-8')
    dataDict = json.loads(dataJSON)
    name = dataDict.get('type_', )
    if name != 'Player':
      return None
    args = dataDict.get('args', )
    keys = ['xf', 'yf', 'zf', 'yaw', 'pitch']
    for (key, val) in zip(keys, args):
      setattr(fromJava.__player_data__, key, val)
    return fromJava.__player_data__
