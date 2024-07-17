"""This file provides the BeginFields and EndFields tags zerotons. These
zerotons may be placed in the top of the class body of a new EZData class.
Between these two tags, all names are expected to be automatic fields.
These must implement the descriptor protocol. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from worktoy.meta import ZerotonMetaclass


class BeginFields(metaclass=ZerotonMetaclass):
  """Marks the beginning of the fields section in the body of an EZData
  class."""


class EndFields(metaclass=ZerotonMetaclass):
  """Marks the end of the fields section in the body of an EZData class."""
