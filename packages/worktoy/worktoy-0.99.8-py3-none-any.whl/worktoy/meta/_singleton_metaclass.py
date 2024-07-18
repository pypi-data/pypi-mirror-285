"""SingletonMetaclass provides a custom metaclass for creating singletons.
These are classes having only one instance, namely the class itself."""
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from worktoy.meta import AbstractMetaclass


class SingletonMetaclass(AbstractMetaclass):
  """SingletonMetaclass provides a custom metaclass for creating singletons.
  These are classes having only one instance, namely the class itself."""

  __singleton_instance__ = None

  def __call__(cls, *args, **kwargs) -> object:
    """The __call__ method is invoked when the class is called."""
    if cls.__singleton_instance__ is None:
      cls.__singleton_instance__ = super().__call__(*args, **kwargs)
    return cls.__singleton_instance__
