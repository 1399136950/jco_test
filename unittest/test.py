import unittest
import os
from HTMLTestRunner import HTMLTestRunner

case_path = os.getcwd() + '\\case'
print(case_path)
suit = unittest.defaultTestLoader.discover(case_path,
                                           pattern='*.py',
                                           top_level_dir=None)

print(suit)
with open('test.html', 'wb') as fd:
    
    runner = HTMLTestRunner(stream=fd)
    runner.run(suit)

