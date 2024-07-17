"""DistributionNamespace provides the namespace object used by the
MetaDistribution metaclass. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from typing import Callable

from worktoy.meta import AbstractNamespace


class DistributionNamespace(AbstractNamespace):
  """DistributionNamespace provides the namespace object used by the
  MetaDistribution metaclass. """

  def jitFactory(self, callMeMaybe: Callable) -> object:
    """This function will create just-in-time compiled distribution
    functions based on the given function. """

  def pdf(self, *names: str) -> Decorator:
    pass
