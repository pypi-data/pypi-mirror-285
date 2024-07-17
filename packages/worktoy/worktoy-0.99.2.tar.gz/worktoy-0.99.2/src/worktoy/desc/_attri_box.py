"""AttriBox subclasses the TypedDescriptor class and incorporates
syntactic sugar for setting the inner class, and for the inner object
creation. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

import sys

from typing import TYPE_CHECKING, Callable, Never

from worktoy.desc import TypedDescriptor, Instance, Owner
from worktoy.text import typeMsg, monoSpace

if sys.version_info.minor < 11:
  from typing_extensions import Self
else:
  from typing import Self

if TYPE_CHECKING:
  pass
else:
  AttriClass = object


class AttriBox(TypedDescriptor):
  """AttriBox subclasses the TypedDescriptor class and incorporates
  syntactic sugar for setting the inner class, and for the inner object
  creation. """

  __positional_args__ = None
  __keyword_args__ = None
  __get_callbacks__ = None
  __set_callbacks__ = None
  __del_callbacks__ = None

  def _getGetCallbacks(self) -> list[Callable]:
    """Getter-function for list of functions to be called on get."""
    if self.__get_callbacks__ is None:
      self.__get_callbacks__ = []
    return self.__get_callbacks__

  def _getSetCallbacks(self) -> list[Callable]:
    """Getter-function for list of functions to be called on set."""
    if self.__set_callbacks__ is None:
      self.__set_callbacks__ = []
    return self.__set_callbacks__

  def _getDelCallbacks(self) -> list[Callable]:
    """Getter-function for list of functions to be called on del."""
    if self.__del_callbacks__ is None:
      self.__del_callbacks__ = []
    return self.__del_callbacks__

  def notifyGet(self, callMeMaybe: Callable) -> Callable:
    """Adds given callable to list of callables to be notified on get."""
    self._getGetCallbacks().append(callMeMaybe)
    return callMeMaybe

  def notifySet(self, callMeMaybe: Callable) -> Callable:
    """Adds given callable to list of callables to be notified on set."""
    self._getSetCallbacks().append(callMeMaybe)
    return callMeMaybe

  def notifyDel(self, callMeMaybe: Callable) -> Callable:
    """Adds given callable to list of callables to be notified on del."""
    self._getDelCallbacks().append(callMeMaybe)
    return callMeMaybe

  def ONGET(self, callMeMaybe: Callable) -> Callable:
    """Decorator for adding a function to the get callbacks."""
    return self.notifyGet(callMeMaybe)

  def ONSET(self, callMeMaybe: Callable) -> Callable:
    """Decorator for adding a function to the set callbacks."""
    return self.notifySet(callMeMaybe)

  def ONDEL(self, callMeMaybe: Callable) -> Callable:
    """Decorator for adding a function to the del callbacks."""
    return self.notifyDel(callMeMaybe)

  def __init__(self, *args, **kwargs) -> None:
    """Initializes the AttriBox instance. """
    TypedDescriptor.__init__(self, *args, **kwargs)
    if not kwargs.get('_root', False):
      e = """The AttriBox class should not be instantiated directly!"""
      raise TypeError(e)
    if not args:
      e = """The inner class must be provided. """
      raise TypeError(e)
    innerClass = args[0]
    if not isinstance(innerClass, type):
      e = typeMsg('innerClass', innerClass, type)
      raise TypeError(e)
    self._setInnerClass(innerClass)

  @classmethod
  def __class_getitem__(cls, innerClass: type) -> Self:
    """Syntactic sugar for setting the inner class. """
    return cls(innerClass, _root=True)

  def __call__(self, *args, **kwargs) -> Self:
    """Syntactic sugar for creating an instance of the inner class. """
    self.__positional_args__ = args
    self.__keyword_args__ = kwargs
    return self

  def _getArgs(self, instance: object) -> list:
    """Returns the arguments used to create the inner object. """
    out = []
    for arg in self.__positional_args__:
      if arg is Instance:
        out.append(instance)
      elif arg is Owner:
        out.append(self._getFieldOwner())
      else:
        out.append(arg)
    return out

  def _getKwargs(self, instance: object) -> dict:
    """Returns the keyword arguments used to create the inner object. """
    out = {}
    for (key, value) in self.__keyword_args__:
      if value is Instance:
        out[key] = instance
      elif value is Owner:
        out[key] = self._getFieldOwner()
      else:
        out[key] = value
    return self.__keyword_args__

  def _createInnerObject(self, instance: object) -> object:
    """Creates an instance of the inner class. """
    innerClass = self._getInnerClass()
    args, kwargs = self._getArgs(instance), self._getKwargs(instance)
    innerObject = innerClass(*args, **kwargs)
    if TYPE_CHECKING:
      assert isinstance(innerObject, AttriClass)
    innerObject.setOuterBox(self)
    innerObject.setOwningInstance(instance)
    innerObject.setFieldOwner(self._getFieldOwner())
    innerObject.setFieldName(self._getFieldName())
    return innerObject

  def __str__(self, ) -> str:
    try:
      fieldName = self._getFieldName()
      ownerName = self._getFieldOwner().__name__
    except AttributeError as attributeError:
      if 'has not been assigned to a field' not in str(attributeError):
        raise attributeError
      ownerName = '(TBD)'
      fieldName = '(TBD)'
    innerName = self._getInnerClass().__name__
    return '%s.%s: %s' % (ownerName, fieldName, innerName)

  def __repr__(self, ) -> str:
    try:
      fieldName = self._getFieldName()
    except AttributeError as attributeError:
      if 'has not been assigned to a field' not in str(attributeError):
        raise attributeError
      fieldName = '(TBD)'
    innerName = self._getInnerClass().__name__
    args = [*self.__positional_args__, *self.__keyword_args__]
    args = ', '.join([str(arg) for arg in args])
    return '%s = AttriBox[%s](%s)' % (fieldName, innerName, args)

  @classmethod
  def _getOwnerListName(cls) -> str:
    """Returns the name at which the list of attribute instances of this
    type. Please note that this name is not unique to the owner as they
    are in separate scopes."""
    return '__boxes_%s__' % cls.__qualname__

  def __set_name__(self, owner: type, name: str) -> None:
    """Sets the name of the field. """
    ownerListName = self._getOwnerListName()
    TypedDescriptor.__set_name__(self, owner, name)
    existing = getattr(owner, ownerListName, [])
    if existing:
      return setattr(owner, ownerListName, [*existing, self])
    setattr(owner, ownerListName, [self, ])
    oldInitSub = getattr(owner, '__init_subclass__')

    def newInitSub(cls, *args, **kwargs) -> None:
      """Triggers the extra init"""
      oldInitSub(*args, **kwargs)
      self.applyBoxes(cls)

    setattr(owner, '__init_subclass__', classmethod(newInitSub))

  @classmethod
  def applyBoxes(cls, owner: type) -> None:
    """Applies the boxes to the owner class."""
    ownerListName = cls._getOwnerListName()
    boxes = getattr(owner, ownerListName, [])
    for box in boxes:
      if not isinstance(box, AttriBox):
        e = typeMsg('box', box, AttriBox)
        raise TypeError(e)
      boxName = box._getFieldName()
      setattr(cls, boxName, box)
      cls.__set_name__(box, owner, boxName)

  def __get__(self, instance: object, owner: type) -> object:
    """The __get__ method is called when the descriptor is accessed via the
    owning instance. """
    value = TypedDescriptor.__get__(self, instance, owner)
    for callback in self._getGetCallbacks():
      callback(instance, value)
    return value

  def __set__(self, instance: object, value: object) -> None:
    """The __set__ method is called when the descriptor is assigned a value
    via the owning instance. """
    pvtName = self._getPrivateName()
    oldValue = getattr(instance, pvtName, None)
    setattr(instance, pvtName, value)
    for callback in self._getSetCallbacks():
      callback(instance, oldValue, value)

  def __delete__(self, instance: object, ) -> Never:
    """Deleter-function not yet implemented!"""
    e = """Tried deleting the '%s' attribute from instance of class '%s', 
    but this deleter-function is not yet implemented!"""
    msg = e % (self._getFieldName(), instance.__class__.__name__)
    raise NotImplementedError(monoSpace(msg))
