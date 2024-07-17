"""The 'yolo' function receives any number of callables and runs them."""
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

import sys
import time
from typing import Callable

from icecream import ic

from worktoy.math import log


def yolo(*args: Callable) -> None:
  """The 'yolo' function receives any number of callables and runs them."""
  tic = time.perf_counter_ns()
  print('Running python script located at: \n%s' % sys.argv[0])
  print('Started at: %s' % time.ctime())
  print(77 * '-')
  retCode = 0
  for callMeMaybe in args:
    print('\nRunning: %s\n' % callMeMaybe.__name__)
    try:
      retCode = callMeMaybe()
    except BaseException as exception:
      print('Exception: %s' % exception)
      retCode = -1
  retCode = 0 if retCode is None else retCode
  print(77 * '-')
  print('Return Code: %s' % retCode)
  toc = int(time.perf_counter_ns() - tic)
  n = 0
  while toc > 1e03:
    toc *= 1e-03
    n += 1
  name = ['nano', 'micro', 'milli', ''][int(n)]
  print('Runtime: %d %s-seconds' % (int(toc), name))
