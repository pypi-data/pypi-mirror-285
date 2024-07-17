"""Vocabulary loads the lorem ipsum words from two files containing
regular words and common words. Please note that those files are not read
at class creation time but when the __get__ on the relevant descriptor
instance is called. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

import os
from random import sample, choices
from typing import Self, Any

from worktoy.desc import AttriBox, EmptyField
from worktoy.parse import maybe
from worktoy.text import monoSpace


class Vocabulary:
  """Vocabulary loads the lorem ipsum words from two files containing
  regular words and common words. Please note that those files are not read
  at class creation time but when the __get__ on the relevant descriptor
  instance is called. """

  __regular_file__ = 'lorem_ipsum.txt'
  __common_file__ = 'lorem_ipsum_common.txt'
  __fallback_regular_count__ = 1
  __fallback_common_count__ = 10
  __reg_count__ = None
  __com_count__ = None
  __iter_contents__ = None

  regCount = EmptyField()
  comCount = EmptyField()

  @regCount.GET
  def _getRegCount(self) -> int:
    """Getter-function for the regular count."""
    return maybe(self.__reg_count__, self.__fallback_regular_count__)

  @regCount.SET
  def _setRegCount(self, count: int) -> None:
    """Setter-function for the regular count."""
    if not isinstance(count, int):
      e = """Expected an integer, but got: %s!"""
      raise TypeError(monoSpace(e % type(count)))
    self.__reg_count__ = count

  @comCount.GET
  def _getComCount(self) -> int:
    """Getter-function for the common count."""
    return maybe(self.__com_count__, self.__fallback_common_count__)

  @comCount.SET
  def _setComCount(self, count: int) -> None:
    """Setter-function for the common count."""
    if not isinstance(count, int):
      e = """Expected an integer, but got: %s!"""
      raise TypeError(monoSpace(e % type(count)))
    self.__com_count__ = count

  @staticmethod
  def _load(fileName: str, ) -> list[str]:
    """The _load method returns the words found in the given file as a
    list. The file is assumed placed in the same directory as the current
    file."""
    here = os.path.dirname(__file__)
    there = os.path.join(here, fileName)
    if not os.path.exists(there):
      e = """Unable to find file: '%s' in directory: '%s'!"""
      raise FileNotFoundError(monoSpace(e % (fileName, here)))
    if not os.path.isfile(there):
      e = """Expected file at '%s', but found a directory!"""
      raise IsADirectoryError(monoSpace(e % os.path.abspath(there)))
    with open(os.path.join(here, fileName), 'r') as file:
      words = file.read()
    return words.split()

  def getRegularWords(self) -> list[str]:
    """Getter-function for the regular words."""
    return self._load(self.__regular_file__)

  def getCommonWords(self) -> list[str]:
    """Getter-function for the common words."""
    return self._load(self.__common_file__)

  def getWords(self, *args) -> list[str]:
    """Getter-function for all words. Optional arguments:
    If one integer is given, the common words are repeated that many times.
    if two integers are given, the common words are repeated as many times
    as the greater and regular words as the lesser. """
    reg, com = self.getRegularWords(), self.getCommonWords()
    return [*reg * self.regCount, *com * self.comCount]

  def getByLen(self, wordLen: int, size: int = None) -> list[str] | str:
    """Getter-function for words of a given length. Optional argument:
    If an integer is given, the list is repeated that many times. """
    size: int = maybe(size, 1)
    words = [word for word in self.getWords() if len(word) == wordLen]
    out = choices(words, k=size)
    if size == 1:
      return out[0]
    return out

  @staticmethod
  def _parseInts(*args) -> list[int]:
    """Parses argument to list of ints"""
    return sorted([arg for arg in args if isinstance(arg, int)])

  def __init__(self, *args) -> None:
    self.regCount, self.comCount = [*self._parseInts(*args), 1, 1][:2]

  def __iter__(self, ) -> Self:
    """Implementation of the iterator protocol."""
    self.__iter_contents__ = [*self.getWords(), ]
    return self

  def __next__(self, ) -> Any:
    """Implementation of the iterator protocol."""
    try:
      return self.__iter_contents__.pop(0)
    except IndexError:
      raise StopIteration
