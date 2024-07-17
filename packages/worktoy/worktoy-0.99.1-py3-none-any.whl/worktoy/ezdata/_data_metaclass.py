"""DataMetaclass provides a custom metaclass for dataclasses. Classes
derived from DataMetaclass should use instances of AttriBox in their class
body to denote data fields. These fields are populated automatically by
the __init__ methods. Derived classes are free to defined methods,
but must not implement the __init__ method as it is reserved for
populating the data fields."""
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from worktoy.meta import AbstractMetaclass
from worktoy.ezdata import DataNamespace


class DataMetaclass(AbstractMetaclass):
  """DataMetaclass provides a custom metaclass for dataclasses. Classes
  derived from DataMetaclass should use instances of AttriBox in their class
  body to denote data fields. These fields are populated automatically by
  the __init__ methods. Derived classes are free to defined methods,
  but must not implement the __init__ method as it is reserved for
  populating the data fields."""

  @classmethod
  def __prepare__(mcls, name: str, _, **kwargs) -> DataNamespace:
    return DataNamespace(mcls, name, (), **kwargs)

  def __str__(cls) -> str:
    """String representation"""
    return cls.__name__


class EZData(metaclass=DataMetaclass):
  """EZData provides a base class for dataclasses. Data fields must be
  instances of AttriBox and the __init__ method is created automatically.
  Subclasses are not allowed to implement the __init__ method. """
