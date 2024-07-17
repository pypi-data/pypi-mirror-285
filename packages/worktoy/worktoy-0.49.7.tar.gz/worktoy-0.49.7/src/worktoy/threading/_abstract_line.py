"""AbstractLine provides an abstract baseclass for the classes intended
for use in a threading loop. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from abc import abstractmethod
from queue import Empty, Queue
from threading import Thread
from typing import TYPE_CHECKING

from worktoy.desc import EmptyField


class AbstractLine(Thread):
  """AbstractLine provides an abstract baseclass for the classes intended
  for use in a threading loop. """

  __fallback_max_fps__ = 60

  __allow_run__ = None
  __max_fps__ = None
  __data_queue__ = None
  __consume_callback__ = None

  if TYPE_CHECKING:
    dataQueue: Queue
  else:
    dataQueue = EmptyField()
    if TYPE_CHECKING:
      assert isinstance(dataQueue, EmptyField)

    @dataQueue.GET
    def _getDataQueue(self, **kwargs) -> Queue:
      """Getter-function for the data queue. """
      if self.__data_queue__ is None:
        if kwargs.get('_recursion', False):
          raise RecursionError
        self._createQueue()
        return self._getDataQueue(_recursion=True)
      if isinstance(self.__data_queue__, Queue):
        return self.__data_queue__

    def _createQueue(self) -> None:
      """Creates the data queue."""
      if self.__data_queue__ is not None:
        e = """The data queue is already created!"""
        raise RuntimeError(e)
      self.__data_queue__ = Queue()

  @abstractmethod
  def setup(self, *args, **kwargs) -> bool:
    """Subclasses should implement this method to perform setup operations
    before the threading loop starts. If successful, this method should
    return True, and the loop will start. If the method returns False,
    an error is raised."""

  @abstractmethod
  def innerLoop(self, *args, **kwargs) -> object:
    """During the loop this main function defines the looping operation.
    The loop calls this method continuously. No return value is expected. """

  @abstractmethod
  def errorHandler(self, exception: BaseException) -> bool:
    """This method is called when an exception is raised in the main loop.
     Subclasses should implement this method to handle exceptions.
     Returning True is taken to mean that the exception is handled and
     that the loop may continue. """

  @abstractmethod
  def consume(self, data: object) -> object:
    """Subclasses may implement this method to receive data from the
    queue."""

  @abstractmethod
  def requestQuit(self) -> None:
    """The requestQuit method is called to request the loop to stop. """

  def start(self, ) -> None:
    """If the setup method returns True, this method will invoke the
    parent method."""
    self.__allow_run__ = True
    if self.setup():
      Thread.start(self)
    else:
      e = """Failed to setup the loop!"""
      raise RuntimeError(e)

  def run(self) -> None:
    """The run method is the main loop. """
    if TYPE_CHECKING:
      assert isinstance(self.dataQueue, Queue)
    while self.__allow_run__:
      try:
        data = self.innerLoop()
      except TimeoutError as timeoutError:
        continue
      if data:
        self.appendQueue(data)
        self.consumeQueue()
      else:
        self.requestQuit()

  def appendQueue(self, data: object) -> None:
    """Appends the data to the queue."""
    self.dataQueue.put(data)

  def consumeQueue(self, ) -> None:
    """Consumes the queue."""
    try:
      self.consume(self.dataQueue.get_nowait())
      return self.consumeQueue()
    except Empty:
      return

  def __init__(self, *args, **kwargs) -> None:
    Thread.__init__(self)
