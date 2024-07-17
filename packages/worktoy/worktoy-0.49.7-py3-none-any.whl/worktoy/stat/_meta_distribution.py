"""MetaDistribution class provides a metaclass for creating probability
distribution classes. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from icecream import ic

from worktoy.meta import AbstractMetaclass, Bases, Space
from worktoy.stat import DistributionNamespace


class MetaDistribution(AbstractMetaclass):
  """MetaDistribution class provides a metaclass for creating probability
  distribution classes. """

  @classmethod
  def __prepare__(mcls, name: str, bases: Bases, **kws) -> Space:
    """The __prepare__ method is invoked before the class is created."""
    return DistributionNamespace(mcls, name, bases, **kws)

  def __new__(mcls, name: str, bases: Bases, space: Space, **kws) -> type:
    """The __new__ method is invoked to create the class."""
    if hasattr(space, 'compile'):
      namespace = space.compile()
    else:
      namespace = space
    cls = AbstractMetaclass.__new__(mcls, name, bases, namespace, **kws)
    setattr(cls, '__name_space__', space)
    return cls

  def __init__(cls, name: str, bases: Bases, space: Space, **kws) -> None:
    """The __init__ method is invoked after the class is created."""
    AbstractMetaclass.__init__(cls, name, bases, space, **kws)

  def __str__(cls) -> str:
    """The __str__ method is invoked when the class is converted to a
    string."""
    return cls.__name__
