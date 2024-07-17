"""KeeNuMeta provides the metaclass for the KeeNum class."""
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Iterable

from worktoy.keenum import KeeNumSpace, KeeNumObject
from worktoy.meta import AbstractMetaclass
from worktoy.parse import maybe
from worktoy.text import typeMsg, stringList


class KeeNumMeta(AbstractMetaclass):
  """KeeNumMeta provides the metaclass for the KeeNum class."""
  __keenum_entries__ = None
  __allow_instantiation__ = None
  __iter_contents__ = None

  def _getKeeNumEntries(cls, ) -> list[KeeNumObject]:
    """Getter-function for the KeeNum entries."""
    entries = maybe(cls.__keenum_entries__, [])
    if isinstance(entries, list):
      for item in entries:
        if not isinstance(item, KeeNumObject):
          e = typeMsg('item', item, KeeNumObject)
          raise TypeError(e)
      return entries
    e = typeMsg('__keenum_entries__', entries, list)
    raise TypeError(e)

  @classmethod
  def __prepare__(mcls, name: str, _, **kwargs) -> KeeNumSpace:
    """The __prepare__ method is invoked before the class is created."""
    return KeeNumSpace(mcls, name, (), **kwargs)

  def __new__(mcls, name: str, _, keeNumSpace: KeeNumSpace, **__) -> type:
    """The __new__ method is invoked to create the class."""
    namespace = keeNumSpace.compile()
    bases = (KeeNumObject,)
    return AbstractMetaclass.__new__(mcls, name, bases, namespace, )

  def __init__(cls, name: str, _, keeNumSpace: KeeNumSpace, **__) -> None:
    """The __init__ method is invoked after the class is created."""
    cls.__allow_instantiation__ = True
    entries = keeNumSpace.getKeeNumEntries()
    newEntries = []
    for entry in entries:
      newEntries.append(cls(entry))
    cls.__keenum_entries__ = newEntries
    cls.__allow_instantiation__ = False
    AbstractMetaclass.__init__(cls, name, (), keeNumSpace, )

  def __call__(cls, *args, **kwargs) -> object:
    """The __call__ method is invoked when the class is called."""
    if cls.__allow_instantiation__:
      return super().__call__(*args, **kwargs)
    return cls._parse(*args, **kwargs)

  def __getitem__(cls, item: object) -> object:
    """The __getitem__ method is invoked when the class is indexed."""
    args, kwargs = (), {}
    if not isinstance(item, (tuple, list)):
      return cls._parse(item)
    if len(item) == 1:
      return cls.__getitem__(item[0])
    if len(item) > 1:
      if isinstance(item[-1], dict):
        args = (*item[:-1],)
        kwargs = item[-1]
      else:
        args = (*item,)
        kwargs = {}
    return cls._parse(*args, **kwargs)

  def _recognizeIndex(cls, index: int) -> object:
    """The recognize method identifies the entry of the given name. If
    None are found, a ValueError is raised. """
    if index < 0 or index >= len(cls):
      return cls._recognizeIndex(index % len(cls))
    for entry in cls._getKeeNumEntries():
      if int(entry) == index:
        return entry
    e = """Unable to recognize KeeNum entry!"""
    raise ValueError(e)

  def _recognizeName(cls, name: str) -> object:
    """The recognize method identifies the entry of the given name. If
    None are found, a ValueError is raised. """
    for entry in cls._getKeeNumEntries():
      if entry.name.lower() == name.lower():
        return entry
    e = """Unable to recognize KeeNum entry!"""
    raise ValueError(e)

  def _parseKwargs(cls, **kwargs) -> object:
    """Parses keyword arguments"""
    if TYPE_CHECKING:
      assert issubclass(cls, KeeNumObject)
    nameKeys = stringList("""name, key, entry""")
    for key in nameKeys:
      if key in kwargs:
        val = kwargs[key]
        if isinstance(val, cls):
          return val
        if isinstance(val, str):
          return cls._recognizeName(val)
        if isinstance(val, int):
          return cls._recognizeIndex(val)
        if isinstance(val, KeeNumObject):
          return cls._recognizeName(val.name)
        e = typeMsg('KeeNumObject', val, KeeNumObject)
        raise TypeError(e)

  def _parseArgs(cls, *args) -> Optional[object]:
    """Parses positional arguments"""
    for arg in args:
      if isinstance(arg, cls):
        return arg
      if isinstance(arg, KeeNumObject):
        return cls._recognizeName(arg.name)
      if isinstance(arg, str):
        return cls._recognizeName(arg)
      if isinstance(arg, int):
        return cls._recognizeIndex(arg)

  def _parse(cls, *args, **kwargs) -> object:
    """The recognize method identifies the entry indicated by the
    arguments. """
    keeNumObject = maybe(cls._parseArgs(*args), cls._parseKwargs(**kwargs))
    if keeNumObject is None:
      e = """Unable to recognize KeeNum entry!"""
      raise ValueError(e)
    if isinstance(keeNumObject, cls):
      return keeNumObject
    e = typeMsg('keeNumObject', keeNumObject, cls)
    raise TypeError(e)

  def __getattr__(cls, key: str | int) -> object:
    """The __getattr__ method is invoked when an attribute is accessed."""
    if isinstance(key, int):
      return cls._recognizeIndex(key)
    if isinstance(key, str):
      return cls._recognizeName(key)
    return object.__getattribute__(cls, key)

  def __len__(cls) -> int:
    """The length of the class is the number of entries"""
    return len(cls._getKeeNumEntries())

  def __contains__(cls, item: object) -> bool:
    """The __contains__ method is invoked when the class is checked for
    membership."""
    try:
      cls._parse(item)
      return True
    except ValueError:
      return False

  def __iter__(cls) -> object:
    """The __iter__ method is invoked when the class is iterated."""
    cls.__iter_contents__ = [*cls._getKeeNumEntries(), ]
    return cls

  def __next__(cls) -> object:
    """The __next__ method is invoked when the class is iterated."""
    try:
      return cls.__iter_contents__.pop(0)
    except IndexError:
      raise StopIteration


class KeeNum(metaclass=KeeNumMeta):
  """KeeNum provides the metaclass for the KeeNum class."""


if TYPE_CHECKING:
  assert isinstance(KeeNum, Iterable)
