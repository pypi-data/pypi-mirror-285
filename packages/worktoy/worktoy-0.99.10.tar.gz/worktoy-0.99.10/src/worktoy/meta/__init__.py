"""The 'worktoy.meta' package provides base classes for working with
metaclasses.

Consider the following class definition:
class SomeClass:
  pass

The above code is equivalent to the following:
class SomeClass(object, metaclass=type):
  pass

The 'metaclass' defaults to 'type' and every object in python is an
instance of 'object', so the above code is equivalent to the first. A
custom metaclass subclasses 'type' allowing for customizing everything about
what it means to be a class in python. This concept is the most powerful tool
in python. This is because any potentially more powerful tool can be
achieved by using a custom metaclass.

Below is an example of a custom metaclass which explicitly does what type
does during the class creation process. This illustrates the power of the
custom metaclass, because each step can be entirely customized.


class MetaClass(type):
  #  MetaClass inherits from 'type' making it a usable as a metaclass.

  @classmethod
  def __prepare__(mcls,
                  name: str,
                  bases: tuple[type, ...],
                  **kwargs) -> dict:
    #  The __prepare__ method is a class method meaning that the first
    #  argument it receives, is the metaclass itself. The classmethod
    # decorator is required by the __prepare__ method. This method creates
    #  the namespace object used during the class creation process. The
    #  default namespace object is an empty instance of 'dict'.
    return dict()

  def __new__(mcls,
              name: str,
              bases: tuple[type, ...],
              namespace: dict,
              **kwargs) -> type:
    #  The __new__ method is a class method meaning that the first
    #  argument it receives, is the metaclass itself. This method creates
    #  the class object. The default class object is an instance of 'type'.
    #  Please note, that while this method is indeed a class method, it must
    #  NOT be decorated with the classmethod decorator. Doing so will result
    #  highly undefined behaviour!
    return type(name, bases, namespace)

  def __init__(cls,
               name: str,
               bases: tuple[type, ...],
               namespace: dict,
               **kwargs) -> type:
    #  The __init__ method is an instance method meaning that the first
    #  argument it receives, is the newly created class returned by the
    #  __new__ method.
    #
    #  The __init__ method on type does nothing, but is still called. This
    #  allows a custom metaclass to perform further initialization after
    #  the class object has been created. This is convenient, because the
    #  descriptor protocol invokes __set_name__ on the variables in the
    #  class body, before the __init__ method is invoked.

  def __call__(cls, *args, **kwargs) -> object:
    #  This method is invoked by 'calling' the class object. Typically,
    #  this creates a new instance of the class. A custom metaclass can
    #  customize this behaviour, for example to create a singleton class.
    #
    #  The default implementation is to create an object by calling the
    #  __new__ method on the class object. Please note, that classes are
    #  able to define __new__ and __init__ methods regardless of their
    #  metaclass.
    self = cls.__new__(cls, *args, **kwargs)
    if isinstance(self, cls):
      cls.__init__(self, *args, **kwargs)
    return self

  def __instancecheck__(cls, instance: object) -> bool:
    #  This method is invoked whenever the builtin 'isinstance' function
    #  is called to check if an object is an instance of a class. The default
    #  implementation compares the __class__ attribute of the instance
    #  against the class object and its bases.
    return True if instance.__class__ in cls.mro() else False

  def __subclasscheck__(cls, subclass: type) -> bool:
    #  This method is invoked whenever the builtin 'issubclass' function
    #  is called. It allows classes derived from the metaclass to determine
    #  if another class is a subclass of it. The default implementation
    #  checks if the potential subclass is in the mro of the class object.
    #  Please note, that by default this method returns True if subclass
    #  is the class object itself. This means that in python, classes are
    #  understood to be subclasses of themselves.
    return True if subclass in cls.mro() else False

  def __subclasses__(cls) -> list[type]:
    #  This method returns a list of all immediate subclasses of the given
    #  class 'cls'. Please note that the default implementation does not work
    #  recursively, meaning that subclasses of subclasses are not included.
    #  Further, the default implementation makes use of a list managed
    #  internally by the Python interpreter itself for internal
    #  bookkeeping purposes.
    return type.__subclasses__(cls)

When a class is created, the following events occur:
0.  The metaclass is created.
1.  The __prepare__ method on the metaclass is called creating the
namespace object.
2.  Each non-empty line in the class body is split into key and value pairs
around the equal sign and passed to the namespace object. This object must be
an instance of dict or a subclass of dict. The __setitem__ method on the
namespace object is then invoked on the key and value:
namespace[key] = value or namespace.__setitem__(key, value).
**IMPORTANT**: Under certain circumstances, a line will not contain an
equal sign. In this case, the __getitem__ method on the namespace object
is called:
namespace[key] or namespace.__getitem__(key)
In this case, the namespace object must raise a KeyError on the key
received. This KeyError is then caught and processed internally by the
interpreter. If the namespace object does not raise a KeyError, HIGHLY
UNDEFINED BEHAVIOUR will result.
3.  The resulting namespace object is passed to the __new__ method along
with the name and base classes of the class along with keyword arguments.
4.  The __new__ method creates and returns the class object.
5.  For each instance in the class body, the __set_name__ method is called.
6.  The __init__ method on the metaclass is called with the class object
as the first argument along with the name, base classes and namespace
object. After this method, the class is created.


"""
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from ._type_names import Bases, Namespace, Space
from ._type_names import FunctionDecorator, ClassDecorator, Decorator
from ._base_object import BaseObject
from ._abstract_namespace import AbstractNamespace
from ._abstract_metaclass import AbstractMetaclass
from ._singleton_metaclass import SingletonMetaclass
from ._zeroton_metaclass import ZerotonMetaclass
