"""This file provide common mathematical functions. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from math import pi

from worktoy.math import Number, jitArcTan, jitLog, jitCos, jitSin, jitExp


def arg(x: Number) -> Number:
  """The argument of a complex number."""
  if not x:
    e = """Tried to determine the argument of zero!"""
    raise ZeroDivisionError(e)
  if isinstance(x, float):
    return 0 if x > 0 else pi

  if not x.imag:
    return arg(x.real)
  if not x.real:
    return pi / 2 if x.imag > 0 else -pi / 2
  if x.real > 0 and x.imag > 0:  # First quadrant
    return jitArcTan(x.imag / x.real)
  if x.real < 0 and x.imag < 0:  # Third quadrant
    return pi - jitArcTan(x.imag / x.real)
  if x.real < 0:  # Second quadrant
    return pi - jitArcTan(x.imag / -x.real)
  return -jitArcTan(-x.imag / x.real)  # Fourth quadrant


def log(x: Number) -> Number:
  """The natural logarithm."""
  if not x:
    e = """Tried to determine the logarithm of zero!"""
    raise ZeroDivisionError(e)
  if isinstance(x, complex):
    return log(abs(x)) + arg(x) * 1j
  if x < 0:
    return log(-x) + pi * 1j
  if x == 1:
    return 0
  if x > 1:
    return -jitLog(1 / x)
  return jitLog(x)


def exp(x: Number) -> Number:
  """The exponential function."""
  if not x:
    return 1
  if isinstance(x, complex):
    r, t = abs(x), arg(x)
    return exp(r) * (jitCos(t) + jitSin(t) * 1j)
  return jitExp(x)
