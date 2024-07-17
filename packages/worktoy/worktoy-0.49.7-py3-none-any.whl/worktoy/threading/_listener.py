"""Listener class receives data. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

import sys
from socket import socket, AF_INET, SOCK_STREAM
from typing import TYPE_CHECKING

from worktoy.desc import AttriBox, EmptyField
from worktoy.text import typeMsg
from worktoy.threading import AbstractLine


class Listener(AbstractLine):
  """Listener class receives data. """

  def consume(self, data: object) -> object:
    print(data)

  __fallback_host__ = 'localhost'
  __fallback_port__ = 42069

  __static_socket__ = None
  __live_socket__ = None
  __live_address__ = None
  __live_error__ = None
  __data_queue__ = None

  port = AttriBox[int](__fallback_port__)
  host = AttriBox[str](__fallback_host__)
  timeLimit = AttriBox[float](5.)

  staticSocket = EmptyField()
  liveSocket = EmptyField()
  liveAddress = EmptyField()

  def __init__(self, *args, **kwargs) -> None:
    """Constructor for the Listener. It parses arguments for host,
    port and callback, the latter of which is passed on to the parent
    class constructor. """
    AbstractLine.__init__(self, *args, **kwargs)

  @staticSocket.GET
  def _getStaticSocket(self, **kwargs) -> socket:
    """Getter-function for the socket. """
    if self.__static_socket__ is None:
      if kwargs.get('_recursion', False):
        raise RecursionError
      self._createSocket()
      return self._getStaticSocket(_recursion=True)
    if isinstance(self.__static_socket__, socket):
      return self.__static_socket__
    e = typeMsg('__inner_socket__', self.__static_socket__, socket)
    raise TypeError(e)

  def _createSocket(self) -> None:
    """Creates the socket."""
    self.__static_socket__ = socket(AF_INET, SOCK_STREAM)
    self.__static_socket__.bind((self.host, self.port))
    self.__static_socket__.listen()

  @liveSocket.GET
  def _getLiveSocket(self) -> socket:
    """Getter-function for the live socket. """
    if self.__live_socket__ is None:
      e = """The live socket is not yet ready!"""
      raise RuntimeError(e)
    if isinstance(self.__live_socket__, socket):
      return self.__live_socket__
    e = typeMsg('__live_socket__', self.__live_socket__, socket)
    raise TypeError(e)

  @liveAddress.GET
  def _getLiveAddress(self, ) -> str:
    """Getter-function for the live address. """
    if self.__live_address__ is None:
      e = """The live address is not yet ready!"""
      raise RuntimeError(e)
    if isinstance(self.__live_address__, bytes):
      return self.__live_address__.decode('utf-8')
    if isinstance(self.__live_address__, str):
      return self.__live_address__
    e = typeMsg('__live_address__', self.__live_address__, str)
    raise TypeError(e)

  def setup(self) -> bool:
    """Sets up the listener"""
    if TYPE_CHECKING:
      assert isinstance(self.staticSocket, socket)
    try:
      conn, addr = self.staticSocket.accept()
    except BaseException as baseException:
      if self.errorHandler(baseException):
        return False
      raise baseException
    self.__live_socket__ = conn
    self.__live_address__ = ': '.join([str(arg) for arg in addr])
    self.__live_socket__.settimeout(5.)
    return True

  def innerLoop(self) -> bytes:
    """The main method waits for a data transmission."""
    if TYPE_CHECKING:
      assert isinstance(self.liveSocket, socket)
    return self.liveSocket.recv(1024)

  def errorHandler(self, exception: BaseException) -> bool:
    """Error handling"""
    if isinstance(exception, ConnectionError):
      return True
    if isinstance(exception, TimeoutError):
      return True
    ("""Exception of type: '%s' caught:""" % type(exception))
    words = str(exception).split()
    line = '#   '
    while words:
      line += words.pop(0)
      if len(line) + len([*words, ''][0]) > 77:
        print(line)
        line = '#   '
    sys.exit(1)

  def requestQuit(self) -> None:
    """The requestQuit method is called to request the loop to stop. """
    if TYPE_CHECKING:
      assert isinstance(self.liveSocket, socket)
      assert isinstance(self.staticSocket, socket)
    self.__allow_run__ = False
    self.liveSocket.close()
    self.staticSocket.close()
