"""Flag provides a boolean descriptor."""
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from worktoy.desc import AbstractDescriptor
from worktoy.parse import maybe


class Flag(AbstractDescriptor):
  """Flag provides a boolean descriptor."""

  __default_value__ = None

  def __init__(self, defVal: bool = None) -> None:
    AbstractDescriptor.__init__(self)
    self.__default_value__ = maybe(defVal, False)

  def __instance_get__(self,
                       instance: object,
                       owner: type,
                       **kwargs) -> object:
    if instance is None:
      return self
    pvtName = self._getPrivateName()
    if getattr(instance, pvtName, None) is None:
      if kwargs.get('_recursion', False):
        raise RecursionError
      setattr(instance, pvtName, self.__default_value__)
      return self.__instance_get__(instance, owner, _recursion=True)
    return True if getattr(instance, pvtName) else False

  def __set__(self, instance: object, value: bool) -> None:
    """Setter-function implementation"""
    pvtName = self._getPrivateName()
    setattr(instance, pvtName, value)
