"""Owner is a Zeroton object indicating the owner of the descriptor
instance.  """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from worktoy.meta import ZerotonMetaclass


class Owner(metaclass=ZerotonMetaclass):
  """Owner is a Zeroton object indicating the class owning the descriptor
  instance.  """


class Instance(metaclass=ZerotonMetaclass):
  """Instance is a Zeroton object indicating the instance owning the
  descriptor instance.  """
