"""MomentField provides a subclass of AttriBox for use by distribution
classes to store the moments defining them. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from typing import Never

from worktoy.desc import AttriBox


class MomentField(AttriBox):
  """MomentField provides a subclass of AttriBox for use by distribution
  classes to store the moments defining them. """

  def _getInnerClass(self, ) -> type:
    """Returns the inner class. """
    return float

  def _setInnerClass(self, *_) -> Never:
    """This subclass disables this setter."""
    fakeName = '_______'
    try:
      return object.__getattribute__(self, fakeName)
    except AttributeError as attributeError:
      err = str(attributeError).replace(fakeName, '_setInnerClass')
      raise AttributeError(err)
