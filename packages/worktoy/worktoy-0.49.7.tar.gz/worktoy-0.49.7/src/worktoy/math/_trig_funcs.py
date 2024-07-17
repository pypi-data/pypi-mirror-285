"""This file provides implementations of trigonometric functions making
use of the numba 'just in time' compiler. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from math import pi

from worktoy.math import jitCos, jitSinh, jitCosh, jitSin

Number = float | complex


def _unitClamp(angle: float) -> float:
  """Clamps to angle to 0 to 2*pi"""
  return angle % (2 * pi)


def cos(angle: Number) -> Number:
  """Smart computation of cosine"""
  if isinstance(angle, complex):
    a = cos(angle.real) * jitCosh(angle.imag)
    b = -sin(angle.real) * jitSinh(angle.imag)
    return a + b * 1j
  angle = _unitClamp(angle)
  if angle > pi:
    return -cos(angle - pi)
  if angle > pi / 2:
    return -cos(pi - angle)
  return jitCos(angle)


def sin(angle: Number) -> Number:
  """Smart computation of sine"""
  if isinstance(angle, complex):
    a = sin(angle.real) * jitCosh(angle.imag)
    b = cos(angle.real) * jitSinh(angle.imag)
    return a + b * 1j
  angle = _unitClamp(angle)
  if angle > pi:
    return -sin(angle - pi)
  if angle > pi / 2:
    return sin(pi - angle)
  return jitSin(angle)


def sec(angle: Number) -> Number:
  """Smart computation of secant"""
  err = False
  if isinstance(angle, complex):
    c = cos(angle)
    if c:
      return 1 / c
    err = True
  if angle % pi == pi / 2 or err:
    e = """Tried to determine secant at odd multiple of pi/2."""
    raise ZeroDivisionError(e)
  return 1 / cos(angle)


def csc(angle: float) -> float:
  """Smart computation of cosecant"""
  if angle % pi == 0:
    e = """Tried to determine cosecant at odd multiple of pi."""
    raise ZeroDivisionError(e)
  return 1 / sin(angle)


def tan(angle: Number) -> Number:
  """Smart computation of tangent"""
  if isinstance(angle, complex):
    s = sin(angle)
    c = cos(angle)
    if c:
      return s / c

  if angle % pi == pi / 2:
    e = """Tried to determine tangent at odd multiple of pi/2."""
    raise ZeroDivisionError(e)
  return sin(angle) / cos(angle)


def cot(angle: float) -> float:
  """Smart computation of cotangent"""
  if not angle % pi:
    e = """Tried to determine cotangent at odd multiple of pi."""
    raise ZeroDivisionError(e)
  return cos(angle) / sin(angle)
