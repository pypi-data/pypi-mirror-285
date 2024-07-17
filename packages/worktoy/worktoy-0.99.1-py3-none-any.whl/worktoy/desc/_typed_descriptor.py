"""TypedDescriptor subclasses DelayedDescriptor and adds to it the inner
class. Instances of this class are desc that return inner objects
belonging to instances of the owning class. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from abc import abstractmethod

from worktoy.desc import DelayedDescriptor, AttriClass
from worktoy.text import typeMsg


class TypedDescriptor(DelayedDescriptor):
  """TypedDescriptor subclasses DelayedDescriptor and adds to it the inner
  class. Instances of this class are desc that return inner objects
  belonging to instances of the owning class. """

  __inner_class__ = None

  def _getInnerClass(self, ) -> type:
    """Returns the inner class. """
    if self.__inner_class__ is None:
      e = """The inner class has not been assigned. """
      raise AttributeError(e)
    if isinstance(self.__inner_class__, type):
      if hasattr(self.__inner_class__, '__ready_box__'):
        return self.__inner_class__
      name = self.__inner_class__.__name__
      bases = (self.__inner_class__,)
      namespace = {**AttriClass.__dict__, }
      return type(name, bases, namespace)
    e = typeMsg('__inner_class__', self.__inner_class__, type)
    raise TypeError(e)

  def _setInnerClass(self, innerClass: type) -> None:
    """Sets the inner class. """
    if self.__inner_class__ is not None:
      e = """The inner class has already been assigned. """
      raise AttributeError(e)
    if not isinstance(innerClass, type):
      e = typeMsg('innerClass', innerClass, type)
      raise TypeError(e)
    self.__inner_class__ = innerClass

  @abstractmethod
  def _createInnerObject(self, instance: object) -> object:
    """Creates an instance of the inner class. """
