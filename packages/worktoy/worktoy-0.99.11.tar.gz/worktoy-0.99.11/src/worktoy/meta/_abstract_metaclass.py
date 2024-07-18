"""AbstractMetaclass provides an abstract baseclass for custom
metaclasses. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from worktoy.meta import AbstractNamespace, Bases, Space, BaseObject


class MetaMetaclass(type):
  """MetaMetaclass is necessary to customize the __str__ method of a
  metaclass"""

  def __str__(cls) -> str:
    return cls.__name__


class AbstractMetaclass(MetaMetaclass, metaclass=MetaMetaclass):
  """The AbstractMetaclass class provides a base class for custom
  metaclasses."""

  @classmethod
  def __prepare__(mcls, name: str, bases: Bases, **kws) -> Space:
    """The __prepare__ method is invoked before the class is created. This
    implementation ensures that the created class has access to the safe
    __init__ and __init_subclass__ through the BaseObject class in its
    method resolution order."""
    if BaseObject in bases:
      return AbstractNamespace(mcls, name, bases, **kws)
    return AbstractNamespace(mcls, name, (*bases, BaseObject,), **kws)

  def __new__(mcls, name: str, bases: Bases, space: Space, **kws) -> type:
    """The __new__ method is invoked to create the class."""
    if hasattr(space, 'compile'):
      space = space.compile()
    return MetaMetaclass.__new__(mcls, name, bases, space, **kws)
