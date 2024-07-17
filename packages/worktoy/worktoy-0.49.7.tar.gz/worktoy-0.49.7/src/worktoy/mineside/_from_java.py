"""FromJava provides a subclass of Listener specialized to receive objects
from Java. Please note that while this does contain dangerous levels of
java-related cringe, it is necessary for Minecraft modding in Python. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

import json
from socket import socket
from typing import TYPE_CHECKING

from worktoy.mineside import Player
from worktoy.threading import Listener


class FromJava(Listener):
  """FromJava provides a subclass of Listener specialized to receive objects
  from Java. Please note that while this does contain dangerous levels of
  java-related cringe, it is necessary for Minecraft modding in Python.

  This subclass implements decoding of bytes objects received from java
  and creates a python object belonging to the appropriate class."""

  __player_data__ = Player()
  __world_status__ = None
  __client_status__ = None

  def innerLoop(self) -> bytes:
    """Reimplementation significantly increasing the maximum supported
    size."""
    if TYPE_CHECKING:
      assert isinstance(self.liveSocket, socket)
    try:
      return self.liveSocket.recv(4096)
    except OSError as osError:
      if isinstance(osError, TimeoutError):
        print(str(osError), type(osError))
        return self.innerLoop()

  def consume(self, data: bytes, ) -> object:
    """Subclasses may implement this method to receive data from the
    queue."""
    try:
      data = json.loads(data.decode('utf-8'))
    except json.JSONDecodeError as jsonError:
      print(str(jsonError), type(jsonError))
      print(data)
      return
    type_ = data.get('type', )
    if type_.lower() == 'command':
      name = data.get('name', )
      args = data.get('args', )
      callMeMaybe = getattr(self, name, )
      return callMeMaybe(*args)

  def setWorldStatus(self, status: bool) -> None:
    """Sets the world status."""
    self.__world_status__ = True if status else False

  def getWorldStatus(self, ) -> bool:
    """Gets the world status."""
    return True if self.__world_status__ else False

  def setClientStatus(self, status: bool) -> None:
    """Sets the client status."""
    self.__client_status__ = True if status else False

  def getClientStatus(self, ) -> bool:
    """Gets the client status."""
    return True if self.__client_status__ else False

  def updatePlayer(self, *args) -> None:
    """Update the player with the new data."""
    if not len(args) == 5:
      raise ValueError('Invalid number of arguments!')
    args = [float(arg) for arg in args]
    self.__player_data__.xf = args[0]
    self.__player_data__.yf = args[1]
    self.__player_data__.zf = args[2]
    self.__player_data__.pitch = args[3]
    self.__player_data__.yaw = args[4]
