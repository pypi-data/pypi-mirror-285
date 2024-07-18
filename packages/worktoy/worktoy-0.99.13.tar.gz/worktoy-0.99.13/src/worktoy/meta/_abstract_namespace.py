"""The AbstractNamespace class provides a base class for namespace classes
used in custom metaclasses. The namespace implements a special method
called 'compile' which creates a regular dictionary object from the
namespace. The AbstractMetaclass.__new__ method uses the 'compile' method
on the namespace object to extract the final namespace object. If the
namespace object received does not implement the compile method,
the namespace object is passed to the super call as it is.

AbstractNamespace implements __getitem__, __setitem__ and __delitem__
methods ensuring compliance with the class creation protocol. The
__setitem__ hooks into the __explicit_set__ method, which subclasses may
reimplement. Please note that __getitem__ and __delitem__ provide no such
hooks. Additionally, AbstractNamespace implements getLines which
returns a list of each line in the class body containing the key,
value pair, or key, error pair."""
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from typing import Self, get_type_hints

from worktoy.parse import maybe
from worktoy.text import typeMsg


class AbstractNamespace(dict):
  """The AbstractNamespace class provides a base class for namespace classes
  used in custom metaclasses."""

  __meta_class__ = None
  __class_name__ = None
  __base_classes__ = None
  __key_args__ = None
  __class_lines__ = None
  __read_only__ = False
  __iter_contents__ = None

  def __init__(self, *args, **kwargs) -> None:
    mcls, name, bases = None, None, None
    for arg in args:
      if isinstance(arg, type) and mcls is None:
        mcls = arg
      elif isinstance(arg, str) and name is None:
        name = arg
      elif isinstance(arg, tuple) and bases is None:
        for base in arg:
          if not isinstance(base, type):
            continue
        bases = [*arg, ]
      if all([i is not None for i in [mcls, name, bases]]):
        break
    self.__meta_class__ = mcls
    self.__class_name__ = name
    self.__base_classes__ = bases
    self.__key_args__ = dict(**kwargs)
    dict.__init__(self, )

  def __explicit_set__(self, key: str, value: object) -> None:
    """The __explicit_set__ method is invoked by __setitem__."""

  def getLines(self) -> list[tuple[str, object]]:
    """The getLines method returns a list of each line in the class body
    containing the key, value pair, or key, error pair."""
    clsLines = maybe(self.__class_lines__, [])
    if isinstance(clsLines, list):
      for entry in clsLines:
        if not isinstance(entry, tuple):
          e = typeMsg('entry', entry, tuple)
          raise TypeError(e)
        if entry:
          if not isinstance(entry[0], str):
            e = typeMsg('key', entry[0], str)
            raise TypeError(e)
          if len(entry) != 2:
            e = """Received unexpected number of elements in entry."""
            raise ValueError(e)
      return clsLines
    e = typeMsg('__class_lines__', clsLines, list)
    raise TypeError(e)

  def _appendLine(self, key: str, value: object) -> None:
    """The _appendLine method appends a key, value pair to the class body."""
    existing = self.getLines()
    self.__class_lines__ = [*existing, (key, value)]

  def __getitem__(self, key: str) -> object:
    """First, attempts to retrieve the value from a previous line. """
    try:
      value = dict.__getitem__(self, key)
    except KeyError as keyError:
      self._appendLine(key, keyError)
      raise keyError
    self._appendLine(key, value)
    return value

  def __setitem__(self, key: str, value: object) -> None:
    oldVal = None
    if dict.__contains__(self, key):
      oldVal = dict.__getitem__(self, key)
    self._appendLine(key, (oldVal, value))
    dict.__setitem__(self, key, value)
    self.__explicit_set__(key, value)

  def __delitem__(self, key: str) -> None:
    if dict.__contains__(self, key):
      oldVal = dict.__getitem__(self, key)
      self._appendLine(key, (oldVal, None))
      return dict.__delitem__(self, key)
    e = """Unable to recognize key: '%s'!""" % key
    raise KeyError(e)

  def __iter__(self, ) -> Self:
    """Implementation of the iteration protocol"""
    lines = self.getLines()
    self.__iter_contents__ = [*lines, ]
    return self

  def __next__(self, ) -> object:
    """Implementation of the next method in the iteration protocol"""
    # ic(self.__iter_contents__)
    try:
      return self.__iter_contents__.pop(0)
    except IndexError:
      raise StopIteration

  def compile(self) -> dict:
    """The compile method creates a regular dictionary object from the
    namespace."""
    return {k: v for (k, v) in dict.items(self, )}

  def getAnnotations(self) -> dict[str, type]:
    """Returns a dictionary mapping attribute name to attribute type. This
    is different from the dictionary stored at key '__annotations__',
    which instead stores the name of type only, because of the use of
    annotations from the future import. """
    val = {}
    if dict.__contains__(self, '__annotations__'):
      val = dict.__getitem__(self, '__annotations__')
    return get_type_hints(type('_', (), {'__annotations__': val})())
