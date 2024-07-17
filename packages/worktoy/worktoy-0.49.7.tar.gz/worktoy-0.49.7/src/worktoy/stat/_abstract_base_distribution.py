"""AbstractBaseDistribution provides a baseclass for statistical
distribution functions. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from numba import float64, jit

from worktoy.stat import MetaDistribution


class AbstractBaseDistribution(metaclass=MetaDistribution):
  """AbstractDistributionFunction provides a baseclass for statistical
  distribution functions. """

  lmao = True

  @jit(nopython=True)
  def pdf(self, ) -> float64:
    """pdf jitted"""
    return 69.420
