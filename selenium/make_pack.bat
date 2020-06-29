pyinstaller testsuit.py -p testcase.py -p testcase_wlx.py -p testcase_hb.py -p testbase.py -p mytelnet.py -F
python make_clean.py
echo %date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2% > exe/version
