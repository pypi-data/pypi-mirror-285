"""The 'joinWords' function joins a list of words into a single string
with appropriate use of commas and 'and'. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations


def joinWords(*words: str) -> str:
  """Join a list of words into a single string with appropriate use of
  commas and 'and'."""
  if not words:
    return ''
  if len(words) == 1:
    if isinstance(words[0], str):
      return words[0]
    raise TypeError
  if len(words) == 2:
    return '%s and %s' % (words[0], words[1])
  return joinWords(', '.join(words[:-1]), words[-1])
