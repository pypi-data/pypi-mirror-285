"""The 'runTests' function runs tests found in the tests directory."""
#  AGPL-3.0 license
#  Copyright (c) 2024 Asger Jon Vistisen
from __future__ import annotations

import os
import unittest


def runTests() -> int:
  """Runs the tests"""
  results = []
  loader = unittest.TestLoader()
  res = None
  for item in os.listdir('tests'):
    if not item.startswith('test'):
      continue
    testPath = os.path.join('tests', item)
    suite = loader.discover(start_dir=testPath, pattern='test*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    res = runner.run(suite)
    if res.wasSuccessful():
      results.append('Tests passed in: %s' % testPath)
    else:
      results.append('Tests failed in: %s' % testPath)
  for result in results:
    print(result)
  if res is None:
    return -1
  return 0
