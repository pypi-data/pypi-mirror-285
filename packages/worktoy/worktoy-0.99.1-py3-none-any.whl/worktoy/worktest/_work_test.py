"""WorkTest provides a general subclass of TestCase"""
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from unittest import TestCase


class WorkTest(TestCase):
  """WorkTest provides a general subclass of TestCase for testing."""

  def __getattribute__(self, key: str) -> object:
    """Careful now!"""
    val = object.__getattribute__(self, key)
    if 'test' in key and False:
      if callable(val):
        clsName = self.__class__.__name__
        print('%s.%s' % (clsName, val.__name__))
    return val

  @classmethod
  def setUpClass(cls, ) -> None:
    """Prints the name of the class"""
    # print('\nBeginning test of class: %s!' % cls.__name__)
