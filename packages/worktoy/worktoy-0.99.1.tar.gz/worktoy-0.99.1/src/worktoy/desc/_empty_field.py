"""EmptyField provides a flexible implementation of the descriptor
protocol allowing owning classes to decorate methods as accessor methods. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from typing import Callable

from worktoy.text import monoSpace, typeMsg


class EmptyField:
  """EmptyField provides a flexible implementation of the descriptor
  protocol allowing owning classes to decorate methods as accessor
  methods. """
  __field_name__ = None
  __field_owner__ = None
  __field_type__ = None
  __getter_name__ = None
  __setter_name__ = None
  __deleter_name__ = None

  def _getFieldName(self) -> str:
    """Returns the name of the field the descriptor is assigned to. """
    if self.__field_name__ is None:
      e = """The descriptor has not been assigned to a field. """
      raise AttributeError(monoSpace(e))
    if isinstance(self.__field_name__, str):
      return self.__field_name__
    e = typeMsg('__field_name__', self.__field_name__, str)
    raise TypeError(monoSpace(e))

  def _getFieldOwner(self) -> type:
    """Returns the type of the class the descriptor is assigned to. """
    if self.__field_owner__ is None:
      e = """The descriptor has not been assigned to a field. """
      raise AttributeError(monoSpace(e))
    if isinstance(self.__field_owner__, type):
      return self.__field_owner__
    e = typeMsg('__field_owner__', self.__field_owner__, type)
    raise TypeError(monoSpace(e))

  def _getOwnerName(self) -> str:
    """Returns the name of the class the descriptor is assigned to. """
    return self._getFieldOwner().__name__

  def _getFieldType(self) -> type:
    """Getter-function for the field type."""
    if self.__field_type__ is None:
      return object
    if isinstance(self.__field_type__, type):
      return self.__field_type__
    e = typeMsg('__field_type__', self.__field_type__, type)
    raise TypeError(e)

  def __set_name__(self, owner: type, name: str) -> None:
    """Set the name of the field and the owner of the field."""
    self.__field_name__ = name
    self.__field_owner__ = owner

  def __get__(self, instance: object, owner: type) -> object:
    """Get the value of the field."""
    if instance is None:
      return self
    if not issubclass(owner, self._getFieldOwner()):
      e = """The instance does not belong to the owner class: '%s'."""
      raise RuntimeError(monoSpace(e % self._getOwnerName()))
    fieldName = self._getFieldName()
    ownerName = self._getOwnerName()
    if self.__getter_name__ is None:
      e = """The field instance at name: '%s' does not have a getter!"""
      raise AttributeError(monoSpace(e % fieldName))
    getter = getattr(owner, self.__getter_name__, None)
    if getter is None:
      e = """The owner class: '%s' does not implement a getter function
      for field: '%s'."""
      raise AttributeError(monoSpace(e % (ownerName, fieldName)))
    if callable(getter):
      return getter(instance)
    e = typeMsg('getter', getter, Callable)
    raise TypeError(e)

  def __set__(self, instance: object, value: object) -> None:
    """Set the value of the field."""
    fieldName = self._getFieldName()
    ownerName = self._getOwnerName()
    if not isinstance(instance, self.__field_owner__):
      e = """The instance does not belong to the owner class: '%s'."""
      raise RuntimeError(monoSpace(e % ownerName))
    if self.__setter_name__ is None:
      e = """The field instance at name: '%s' does not have a setter!"""
      raise AttributeError(monoSpace(e % fieldName))
    setter = getattr(self.__field_owner__, self.__setter_name__, None)
    if setter is None:
      e = """The owner class: '%s' does not implement a setter function
      for field: '%s'."""
      raise AttributeError(monoSpace(e % (ownerName, fieldName)))
    if callable(setter):
      return setter(instance, value)
    e = typeMsg('setter', setter, Callable)
    raise TypeError(e)

  def __delete__(self, instance: object) -> None:
    """Delete the value of the field."""
    fieldName = self._getFieldName()
    ownerName = self._getOwnerName()
    if not isinstance(instance, self.__field_owner__):
      e = """The instance does not belong to the owner class: '%s'."""
      raise RuntimeError(monoSpace(e % ownerName))
    if self.__deleter_name__ is None:
      e = """The field instance at name: '%s' does not have a deleter!"""
      raise AttributeError(monoSpace(e % fieldName))
    deleter = getattr(self.__field_owner__, self.__deleter_name__, None)
    if deleter is None:
      e = """The owner class: '%s' does not implement a deleter function
      for field: '%s'."""
      raise AttributeError(monoSpace(e % (ownerName, fieldName)))
    if callable(deleter):
      return deleter(instance)
    e = typeMsg('deleter', deleter, Callable)
    raise TypeError(e)

  def __set_getter__(self, callMeMaybe: Callable) -> Callable:
    """Set the getter function of the field."""
    self.__getter_name__ = callMeMaybe.__name__
    return callMeMaybe

  def __set_setter__(self, callMeMaybe: Callable) -> Callable:
    """Set the setter function of the field."""
    self.__setter_name__ = callMeMaybe.__name__
    return callMeMaybe

  def __set_deleter__(self, callMeMaybe: Callable) -> Callable:
    """Set the deleter function of the field."""
    self.__deleter_name__ = callMeMaybe.__name__
    return callMeMaybe

  def GET(self, callMeMaybe: Callable) -> Callable:
    """Decorator for setting the getter function of the field."""
    return self.__set_getter__(callMeMaybe)

  def SET(self, callMeMaybe: Callable) -> Callable:
    """Decorator for setting the setter function of the field."""
    return self.__set_setter__(callMeMaybe)

  def DELETE(self, callMeMaybe: Callable) -> Callable:
    """Decorator for setting the deleter function of the field."""
    return self.__set_deleter__(callMeMaybe)

  def DEL(self, callMeMaybe: Callable) -> Callable:
    """Decorator for setting the deleter function of the field."""
    return self.__set_deleter__(callMeMaybe)
