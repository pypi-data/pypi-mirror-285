"""ConstantType provides a zeroton representation of mathematical
constants. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from worktoy.meta import SingletonMetaclass


class MetaConstantType(SingletonMetaclass):
  """This class provides the metaclass for the creation of singleton class
  representations of mathematical constants. Classes should implement
  a getValue method defining a method to compute the value. This method
  can just return a hardcoded value."""

  def __new__(mcls, name: str, _, space: dict[str, object]) -> type:
    """The __new__ method is invoked to create the class."""
