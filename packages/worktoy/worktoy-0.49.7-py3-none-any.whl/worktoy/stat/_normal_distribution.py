"""NormalDistribution encapsulates a normally distributed random variable."""
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

from worktoy.desc import AttriBox, Instance
from worktoy.text import stringList, typeMsg


class NormalDistribution:
  """NormalDistribution encapsulates a normally distributed random
  variable."""

  expectedValue = AttriBox[float](0)
  standardDeviation = AttriBox[float](1)
  pdf = AttriBox[object](Instance)

  def __init__(self, *args, **kwargs) -> None:
    expKeys = stringList("""expectedValue, expected value, mean, mu""")
    stdKeys = stringList("""standardDeviation, standard deviation, sigma""")
    types = dict(expectedValue=float, standardDeviation=float)
    values = {}
    defaultValues = dict(expectedValue=0, standardDeviation=1)
    unusedArgs = [*args, ]
    KEYS = [expKeys, stdKeys]
    for ((name, type_), keys) in zip(types.items(), KEYS):
      for key in keys:
        if key in kwargs:
          val = kwargs[key]
          if isinstance(val, type_):
            values[name] = val
            break
          e = typeMsg(key, val, type_)
          raise TypeError(e)
      else:
        tempArgs = [*unusedArgs, ]
        unusedArgs = []
        for (i, arg) in enumerate(tempArgs):
          if isinstance(arg, type_):
            values[name] = arg
            if i + 1 < len(tempArgs):
              unusedArgs = [*unusedArgs, *tempArgs[i + 1:]]
            break
          else:
            unusedArgs.append(arg)
        else:
          values[name] = defaultValues[name]
    self.expectedValue = values['expectedValue']
    self.standardDeviation = values['standardDeviation']
