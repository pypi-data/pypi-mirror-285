"""KeeNumSpace provides the namespace for the KeeNuMeta class."""
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from worktoy.keenum import KeeNumObject
from worktoy.meta import AbstractNamespace
from worktoy.parse import maybe
from worktoy.text import typeMsg


def auto(*args) -> KeeNumObject:
  """Creates an entry in the KeeNum class."""
  keeNumObject = KeeNumObject()
  if args:
    if len(args) == 1:
      keeNumObject.value = args[0]
    else:
      keeNumObject.value = (*args,)
  return keeNumObject


class KeeNumSpace(AbstractNamespace):
  """KeeNumSpace is a Zeroton object indicating the class owning the
  descriptor instance."""

  __keenum_entries__ = None

  def getKeeNumEntries(self) -> list[KeeNumObject]:
    """Getter-function for the KeeNum entries."""
    out = maybe(self.__keenum_entries__, [])
    if isinstance(out, list):
      for item in out:
        if not isinstance(item, KeeNumObject):
          e = typeMsg('item', item, KeeNumObject)
          raise TypeError(e)
      return out
    e = typeMsg('__keenum_entries__', out, list)
    raise TypeError(e)

  def __explicit_set__(self, key: str, value: object) -> None:
    """The __explicit_set__ method is invoked by __setitem__."""
    if key == '__init__':
      e = """The __init__ method is reserved for KeeNum classes!"""
      raise AttributeError(e)
    if isinstance(value, KeeNumObject):
      key = key.upper()
      entries = self.getKeeNumEntries()
      value._pvtVal = len(entries)
      value.name = key
      if value.value is None:
        value.value = key
      self.__keenum_entries__ = [*entries, value]

  def compile(self) -> dict:
    """The compile method returns the namespace without the KeeNumObjects."""
    out = {}
    entries = self.getKeeNumEntries()
    for key, value in self.items():
      if value in entries:
        continue
      out[key] = value
    return out
