"""The ZerotonMetaclass provides a custom metaclass for creation of Token
objects. They are like singletons, but since they never instantiate,
they are called zerotons. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from typing import Never

from worktoy.meta import AbstractMetaclass


class ZerotonMetaclass(AbstractMetaclass):
  """ZerotonMetaclass provides a custom metaclass for creation of Token
  objects. They are like singletons, but since they never instantiate,
  they are called zerotons. """

  def __new__(mcls, name: str, _, space: dict[str, object]) -> type:
    """The __new__ method is invoked to create the class."""
    cls = super().__new__(mcls, name, (), space)
    return cls

  def __call__(cls, *__, **_) -> Never:
    """The __call__ method is invoked when the class is called."""
    e = """%s is a zeroton and cannot be instantiated!""" % cls.__name__
    raise TypeError(e)

  def __eq__(cls, other: object) -> bool:
    """The __eq__ method is invoked when the class is compared
    with another object."""
    if isinstance(other, str):
      return False if cls.__name__ != other else True
    return False if hash(cls) - hash(other) else True

  def __hash__(cls, ) -> int:
    """Obtaining the hash value of the class name"""
    return str.__hash__(cls.__name__)
