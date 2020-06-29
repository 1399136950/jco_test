import os
import sys

stdout = 'stdout.log'
with open(stdout, 'ab+', 0) as fd:
    os.dup2(sys.stdout.fileno(), fd.fileno())
