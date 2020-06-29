#!/bin/bash

pyinstaller testsuit.py -p testcase.py -p testcase_wlx.py -p testcase_hb.py -p testbase.py -p mytelnet.py -F
python make_clean.py
echo `date +'%Y-%m-%d %H:%M:%S'` > exe/version
