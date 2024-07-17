"""BaseObject is used by AbstractMetaclass as a common baseclass for all
derived classes. All python classes are fundamentally subclasses of the
'object' class. However, two methods on the 'object' class, cause
problems. As of python 3.12.4, both '__init_subclass__' and '__init__'
will raise errors if invoked with arguments other than the subclass or
self respectively. While this is not without merit, flexible signatures
allowing arbitrary positional or keyword arguments are a common pattern.


class ParentClass:
  #  Base class example not implementing __init__ nor __init_subclass__.

class ChildClass(ParentClass):
  #  Child class which does implement __init__.

  def __init__(self, name: str=None, *args, **kwargs) -> None:
    self.name = 'unnamed' if name is None else name
    super().__init__(*args, **kwargs)  # This may raise an error

When instantiating the ChildClass, it will likely be working as expected.
But suppose a further subclass receives additional arguments:


class GrandChildClass(ChildClass):
  # Inspecting the code below would suggest that the __init__ method
  # is flexible enough to handle arbitrary positional arguments.

  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)

Now consider:
someChild = GrandChildClass('Bob')  # No problem
anotherChild = GrandChildClass('Grace', 69)  # This will raise an error,
but why?

ChildClass('Grace', 69) leads to:
  anotherChild = GrandChildClass.__new__(GrandChildClass, 'Grace', 69)
  GrandChildClass.__init__(anotherChild, 'Grace', 69)
  #  The super call reaches the ChildClass:
  ChildClass.__init__(anotherChild, 'Grace', 69)
  #  Since ParentClass does not implement __init__, the super call instead
  #  invokes the __init__ on the first class in the method resolution order.
  #  Since ParentClass have no explicit baseclasses, this means 'object'.
  #  Thus:
  object.__init__(anotherChild, 69)
  #  But this leads to:
  #  'Exception: object.__init__() takes exactly one argument (the
  #  instance to initialize)'


A similar issues happen when applying keyword arguments (other than
metaclass=...) to the class creation, unless it is a baseclass of a class
that implements __init_subclass__. For example:

class SomeMeta(type):  # metaclass
  #  This metaclass tries to apply keyword arguments to the class after it
  #  is initialized.

  def __new__(mcls, name, bases, namespace, **kwargs) -> type:
    #  This method is included for illustration. The implementation is
    #  implements the same functionality as the default.
    return type.__new__(mcls, name, bases, namespace, **kwargs)

  def __init__(cls, name, bases, namespace, **kwargs) -> None:
    #  This method is called after the class object has been created.
    super().__init__(name, bases, namespace)
    for (key, val) in kwargs.items():
      setattr(cls, key, val)


class SomeClass(metaclass=SomeMeta, lmao=True):
  pass


In the previous example, the error message occurs when attempting to
instantiate the classes. But the above example will raise an error during
class creation itself:

"SomeClass.__init_subclass__() takes no keyword arguments"

To make use of keyword arguments during class creation, the functionality
must be implemented at the metaclass level. For example as in the above
example where the __init__ tries to apply the keyword arguments to the
newly created class. Even so, the above error still occurs. This error is
raised by the __new__ method in the metaclass when it calls the __new__
method on the 'type'. This means that in order to make use of keyword
arguments in class creation, not even a custom metaclass is sufficient.
The created class must also have as base class that implements
__init_subclass__ and stops the keyword arguments from reaching
object.__init_subclass__.

While there is merit in ensuring processing of arguments, this is
currently achieved at the expense of significant flexibility. For this
reason, the AbstractMetaclass will make use of the BaseObject class.
Please note, that the default implementations replaced are empty except
for raising the errors explained. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations


class BaseObject:
  """BaseObject provides argument-tolerant implementations of __init__ and
  __init_subclass__ preventing the errors explained in the documentation."""

  def __init__(self, *args, **kwargs) -> None:
    """Why are we still here?"""

  def __init_subclass__(cls, *args, **kwargs) -> None:
    """Just to suffer?"""
