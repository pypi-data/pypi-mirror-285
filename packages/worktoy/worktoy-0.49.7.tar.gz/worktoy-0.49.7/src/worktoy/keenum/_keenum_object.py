"""KeeNumObject provides the base class for all KeeNum classes. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from typing import Self

from worktoy.desc import EmptyField
from worktoy.text import typeMsg


class KeeNumObject:
  """KeeNumObject is the base class for all KeeNum classes. """

  __keenum_name__ = None
  __private_value__ = None
  __public_value__ = None

  name = EmptyField()
  _pvtVal = EmptyField()
  value = EmptyField()

  @name.GET
  def _getName(self) -> object:
    """Getter-function for the name."""
    if self.__keenum_name__ is None:
      e = """The name has not been assigned!"""
      raise AttributeError(e)
    if isinstance(self.__keenum_name__, str):
      return self.__keenum_name__
    e = typeMsg('__keenum_name__', self.__keenum_name__, str)
    raise TypeError(e)

  @name.SET
  def _setName(self, name: str) -> None:
    """Setter-function for the name."""
    if self.__keenum_name__ is not None:
      e = """The name has already been assigned!"""
      raise AttributeError(e)
    if not isinstance(name, str):
      e = typeMsg('name', name, str)
      raise TypeError(e)
    self.__keenum_name__ = name

  @_pvtVal.GET
  def _getPvtVal(self) -> object:
    """Getter-function for the private value."""
    if self.__private_value__ is None:
      e = """The private value has not been assigned!"""
      raise AttributeError(e)
    if isinstance(self.__private_value__, int):
      return self.__private_value__
    e = typeMsg('__private_value__', self.__private_value__, int)
    raise TypeError(e)

  @_pvtVal.SET
  def _setPvtVal(self, privateValue: int) -> None:
    """Setter-function for the private value."""
    if self.__private_value__ is not None:
      e = """The private value has already been assigned!"""
      raise AttributeError(e)
    if not isinstance(privateValue, int):
      e = typeMsg('privateValue', privateValue, int)
      raise TypeError(e)
    self.__private_value__ = privateValue

  @value.GET
  def _getPubVal(self) -> object:
    """Getter-function for the public value."""
    return self.__public_value__

  @value.SET
  def _setPubVal(self, publicValue: object) -> None:
    """Setter-function for the public value."""
    if self.__public_value__ is not None:
      e = """The public value has already been assigned!"""
      raise AttributeError(e)
    self.__public_value__ = publicValue

  def __init__(self, *args, ) -> None:
    for arg in args:
      if isinstance(arg, KeeNumObject):
        self.__keenum_name__ = arg.name
        self.__private_value__ = arg._pvtVal
        self.__public_value__ = arg.value
        break

  def __init_subclass__(cls, **kwargs) -> None:
    """Why are we still here? Just to suffer? Or to raise errors?"""

  def __str__(self) -> str:
    """String representation"""
    return '%s.%s' % (self.__class__.__name__, self.name)

  def __int__(self) -> int:
    """Exposes the private value"""
    if isinstance(self.__private_value__, int):
      return self.__private_value__
    e = typeMsg('__private_value__', self.__private_value__, int)
    raise TypeError(e)

  def __add__(self, other: object) -> Self:
    """Implements addition"""
    if isinstance(other, int):
      return self.__class__(int(self) + other)
    if isinstance(other, KeeNumObject):
      return self + int(other)
    return NotImplemented

  def __sub__(self, other: object) -> Self:
    """Implements subtraction"""
    if isinstance(other, int):
      return self.__class__(int(self) - other)
    if isinstance(other, KeeNumObject):
      return self - int(other)
    return NotImplemented

  def __eq__(self, other: object) -> bool:
    """Implementation of equal operator"""
    if isinstance(other, int):
      return False if int(self) - other else True
    if isinstance(other, KeeNumObject):
      return self == int(other)
    if isinstance(other, self.__class__):
      return self == int(other)
    return NotImplemented
