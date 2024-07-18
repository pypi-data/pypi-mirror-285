"""The stubGen function receives a class and creates an appropriate stub
file. """
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

import builtins
from inspect import getfile

from worktoy.text import monoSpace


def stubGen(cls: type) -> None:
  """The stubGen function receives a class and creates an appropriate stub
  file. """

  boxes = {}
  for (key, val) in cls.__dict__.items():
    if val.__class__.__name__ == 'AttriBox':
      boxes = {**boxes, **{key: val}}
  stubHead = """
               \"\"\"AUTO-GENERATED STUB FILE!\"\"\"<br>
               #  AGPL-3.0 license<br>
               #  Copyright (c) 2024 Asger Jon Vistisen<br>
               from __future__ import annotations<br>"""
  stubClass = """<br><br>class <CLASS_NAME><BASES>:<br>
               <tab>\"\"\"<DOCSTRING>\"\"\""""
  stubLine = """<tab>%s: %s"""
  importLine = """from %s import %s"""
  importLines = []
  if cls.__bases__:
    bases = '(%s)' % ', '.join([base.__name__ for base in cls.__bases__])
    stubClass = stubClass.replace('<BASES>', bases)
    for base in cls.__bases__:
      module = base.__module__
      if module.split('.')[-1].startswith('_'):
        module = '.'.join(module.split('.')[:-1])
      importLines.append(importLine % (module, base.__name__))
  stubClass = stubClass.replace('<CLASS_NAME>', cls.__name__)
  stubClass = stubClass.replace('<DOCSTRING>', cls.__doc__)
  stubLines = []
  importedTypes = [v for (k, v) in builtins.__dict__.items()]
  for (boxName, box) in boxes.items():
    boxType = box.getInnerClass(_raw=True)
    if boxType not in importedTypes:
      module = boxType.__module__
      if module.split('.')[-1].startswith('_'):
        module = '.'.join(module.split('.')[:-1])
      importLines.append(importLine % (module, boxType.__name__))
      importedTypes.append(boxType)
    stubLines.append(stubLine % (boxName, boxType.__name__))
  stubBody = '<br>'.join(stubLines)
  importBody = '<br>'.join(importLines)
  if not importBody:
    stubClass = stubClass.replace('<br><br>', '')
  stubCode = '<br>'.join([stubHead, importBody, stubClass, stubBody])
  stubFile = getfile(cls).replace('.py', '.pyi')
  with open(stubFile, 'w') as file:
    file.write(monoSpace(stubCode))
