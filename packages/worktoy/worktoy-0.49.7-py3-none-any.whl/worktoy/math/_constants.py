"""This file contains common mathematical constants."""
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from worktoy.math import jitArcTan

pi: float = float()
e: float = float()
gamma: float = float()

if __name__ != "__main__":
  pi = 4 * sum([44 * jitArcTan(1 / 57),
                7 * jitArcTan(1 / 239),
                -12 * jitArcTan(1 / 682),
                24 * jitArcTan(1 / 12943)])
