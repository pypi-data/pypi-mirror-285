"""AttriClass provides a minimal class that is ready for boxing. If a
custom class is intended to be used in AttriBox, it may subclass
AttriClass which will provide the necessary methods and attributes. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from worktoy.text import typeMsg


class AttriClass:
  """AttriClass provides a minimal class that is ready for boxing. If a
  custom class is intended to be used in AttriBox, it may subclass
  AttriClass which will provide the necessary methods and attributes. """

  __ready_box__ = True
  __outer_box__ = None
  __owning_instance__ = None
  __field_owner__ = None
  __field_name__ = None

  def getFieldOwner(self) -> type:
    """Getter-function for the field owner. """
    return self.__field_owner__

  def setFieldOwner(self, owner: type) -> None:
    """Setter-function for the field owner. """
    if self.__field_owner__ is not None:
      e = """The field owner has already been assigned!"""
      raise AttributeError(e)
    if isinstance(owner, type):
      self.__field_owner__ = owner
    else:
      e = typeMsg('owner', owner, type)
      raise TypeError(e)

  def getFieldName(self) -> str:
    """Getter-function for the field name. """
    return self.__field_name__

  def setFieldName(self, name: str) -> None:
    """Setter-function for the field name. """
    if self.__field_name__ is not None:
      e = """The field name has already been assigned!"""
      raise AttributeError(e)
    if isinstance(name, str):
      self.__field_name__ = name
    else:
      e = typeMsg('name', name, str)
      raise TypeError(e)

  def getOwningInstance(self) -> object:
    """Getter-function for the owning instance. """
    return self.__owning_instance__

  def setOwningInstance(self, instance: object) -> None:
    """Setter-function for the owning instance. """
    if self.__owning_instance__ is not None:
      e = """The owning instance has already been assigned!"""
      raise AttributeError(e)
    self.__owning_instance__ = instance

  def getOuterBox(self, ) -> object:
    """Getter-function for the outer box. """
    return self.__outer_box__

  def setOuterBox(self, box: object) -> None:
    """Setter-function for the outer box. """
    if self.__outer_box__ is not None:
      e = """The outer box has already been assigned!"""
      raise AttributeError(e)
    self.__outer_box__ = box
