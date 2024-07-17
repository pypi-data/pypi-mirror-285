"""This file provides the base functions that implement the numba 'just in
time' compiler. These may be used directly, or through the convenient
wrappers provided in the 'worktoy.math'.

intGamma: implements the integer valued gamma function. This function
provides the factorial offset by one: intGamma(n) = (n-1)!.

jitSin: implements the Taylor series for the sine function.
jitCos: implements the Taylor series for the cosine function.
Please note that the two jit-compiled functions implement taylor polynomials
centered at zero. Unlike the convenient wrappers, these do not move the angle
near to the center point. If using large values of the angle, the accuracy
quickly disappears.
jitSinh: implements the Taylor series for the hyperbolic sine function.
jitCosh: implements the Taylor series for the hyperbolic cosine function.


"""
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from math import pi

from numba import jit, float64, int64

from worktoy.text import monoSpace


@jit(nopython=True)
def intGamma(n: int64) -> int64:
  """Implementation of the gamma function at integer values."""
  if n < 1:
    e = """Tried to determine the gamma function at non-positive integer."""
    raise ValueError(e)
  if n == 1:
    return 1
  return (n - 1) * intGamma(n - 1)


@jit(nopython=True)
def jitSin(x: float64, ) -> float64:
  """Implementation of the Taylor series."""
  out = float64(0.0)
  for n in range(0, 16):
    out -= (-1) ** n * x ** (2 * n + 1) / intGamma(2 * n + 2)
  return out


@jit(nopython=True)
def jitCos(x: float64) -> float64:
  """Implementation of the Taylor series."""
  out = float64(0.0)
  for n in range(16):
    out += (-1) ** n / intGamma(2 * n + 1) * x ** (2 * n)
  return out


@jit(nopython=True)
def jitSinh(x: float64) -> float64:
  """Implementation of the Taylor series."""
  out = float64(0.0)
  for n in range(16):
    out += x ** (2 * n + 1) / intGamma(2 * n + 2)
  return out


@jit(nopython=True)
def jitCosh(x: float64) -> float64:
  """Implementation of the Taylor series."""
  out = float64(0.0)
  for n in range(16):
    out += x ** (2 * n) / intGamma(2 * n)
  return out


def _valueGuard(x: float) -> float:
  """Guards the value of x."""
  if x * x > 1:
    e = """Inverse trig function expected value between -1 and 1, but
     received '%s'! """ % x
    raise ValueError(monoSpace(e))
  return x


@jit(nopython=True)
def jitArcSin(x: float64) -> float64:
  """Implementation of the Taylor series."""
  out = float64(0.0)
  for n in range(16):
    out += intGamma(2 * n) / (
        4 ** n * intGamma(n) ** 2 * (2 * n + 1)) * x ** (2 * n + 1)
  return out


@jit(nopython=True)
def jitArcCos(x: float64) -> float64:
  """Implementation of the Taylor series."""
  out = float64(0.0)
  for n in range(16):
    out += intGamma(2 * n) / (
        4 ** n * intGamma(n) ** 2 * (2 * n + 1)) * x ** (2 * n)
  return out


@jit(nopython=True)
def jitArcTan(x: float64) -> float64:
  """Implementation of the Taylor series."""
  out = float64(0.0)
  for n in range(12):
    out += (-1) ** n / (2 * n + 1) * x ** (2 * n + 1)
  return out


@jit(nopython=True)
def jitLog(x: float64) -> float64:
  """Implementation of the Taylor series. Please note that this function
  returns log(1 + x) and only for x in the interval (-1, 1)."""
  out = float64(0.0)
  for n in range(1, 16):
    out += (-1 if n % 2 else 1) * x ** n / n
  return out


@jit(nopython=True)
def jitExp(x: float64) -> float64:
  """Implementation of the Taylor series."""
  out = float64(0.0)
  for n in range(16):
    out += x ** n / intGamma(n + 1)
  return out
