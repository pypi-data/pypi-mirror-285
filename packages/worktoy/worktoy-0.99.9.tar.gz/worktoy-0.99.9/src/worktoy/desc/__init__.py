"""The 'worktoy.desc' implements the descriptor protocol with lazy
instantiation. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from ._owner_instance import Owner, Instance
from ._attri_class import AttriClass
from ._empty_field import EmptyField
from ._abstract_descriptor import AbstractDescriptor
from ._flag import Flag
from ._delayed_descriptor import DelayedDescriptor
from ._typed_descriptor import TypedDescriptor
from ._attri_box import AttriBox
