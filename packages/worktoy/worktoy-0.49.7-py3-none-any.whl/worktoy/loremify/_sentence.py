"""Sentence class creates a sample sentence from the words in the
vocabulary that encapsulates the lorem ipsum generation."""
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from worktoy.desc import AttriBox
from worktoy.loremify import Vocabulary
from worktoy.text import monoSpace


class Sentence:
  """Sentence class creates a sample sentence from the words in the
  vocabulary that encapsulates the lorem ipsum generation."""

  __fallback_count__ = 600

  vocabulary = AttriBox[Vocabulary]()
  count = AttriBox[int]()

  @staticmethod
  def _commaChance(*args) -> float:
    """Receives number of words and commas since start of sentence and
    returns probability of placing a comma. """
    intArgs = [arg for arg in args if isinstance(arg, int)]
    if not intArgs:
      e = """Unable to parse required argument specifying number of words!"""
      raise ValueError(monoSpace(e))
    words, commas = [*intArgs, 0][:2]
    mean = 50
    stdDev = 10

  def __init__(self, *args) -> None:
    intArgs = [arg for arg in args if isinstance(arg, int)]
    self.count = [*intArgs, self.__fallback_count__][0]
