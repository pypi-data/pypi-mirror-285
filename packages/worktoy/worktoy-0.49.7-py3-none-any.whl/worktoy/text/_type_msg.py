"""The 'typeMsg' function generates a structured error message when an
object with a given name does not belong to the given type.

Example:

  def square(number: int) -> int:
    #  The function expects an integer as argument
    if not isinstance(number, int):
      e = typeMsg('number', number, int)
      raise TypeError(e)
    return number ** 2

  square(69.420)



"""
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from worktoy.text import monoSpace


def typeMsg(name: str, obj: object, type_: type) -> str:
  """The 'typeMsg' function generates a structured error message when an
  object with a given name does not belong to the given type."""
  expectedType = type_.__name__
  actualType = type(obj).__name__
  e = """Expected object '%s' to be of type '%s', but found '%s' of type 
  '%s'!"""
  return monoSpace(e % (name, expectedType, str(obj), actualType))
