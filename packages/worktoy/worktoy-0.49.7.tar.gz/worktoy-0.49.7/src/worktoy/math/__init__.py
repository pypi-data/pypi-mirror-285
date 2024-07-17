"""The 'worktoy.math' package provides implementations of commonly used
mathematical functions."""
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from ._base_types import Number
from ._jit_functions import intGamma, jitSin, jitCos, jitSinh, jitCosh
from ._jit_functions import jitArcCos, jitArcSin, jitArcTan, jitLog, jitExp
from ._constants import pi
from ._functions import arg, log, exp
