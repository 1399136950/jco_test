#!/usr/bin/python3

import os
from time import sleep
import socket
import queue
import threading
import sys
import signal
import atexit
import time
import re


now_time = lambda: time.strftime('%Y-%m-%d %H:%M:%S')

def echo(q):
    rule='^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'
    while True:
        con,host = q.get()
        con.settimeout(10)
        #print(now_time(), con, host)
        try:
            info = con.recv(4096).decode().strip('\n')
        except:
            pass
        else:
            arr = info.split(',')
            is_set_time = False
            print('[{}] {} {}'.format(now_time(), host, info))
            if re.match('^\d+$', arr[0]):   # 过滤非数字的ID 
                with lock:
                    if len(arr) == 2:
                        new_time = arr[1]
                        if re.match(rule, new_time):
                            is_set_time = True
                            cmd = "date +'%Y-%m-%d %H:%M:%S'"
                            old_time = os.popen(cmd).read().strip('\n')
                            cmd = "date -s '{}'".format( new_time )
                            # 设置新时间
                            os.popen(cmd).read()
                    cmd = 'xkcd ' + arr[0]
            
                    res = os.popen(cmd).read()
                    passwd = re.findall('passwd:(.*)$', res)[0]
                    # 将时间设置回原来
                    if is_set_time:
                        cmd  = "date -s '{}'".format( old_time )
                        os.popen(cmd).read()
                con.send(passwd.encode())
            else:
                con.send('input id error'.encode())
        finally:
            con.close()

def echo_server():
    if os.fork() > 0:
        exit(0)
    os.chdir('/')
    os.umask(0o777)
    os.setsid()
    if os.fork() > 0:
        exit(0)
    pid_file = '/tmp/pid.tmp'
    print( 'start with pid', os.getpid() )
    with open(pid_file, 'w') as fd:
        fd.write( str( os.getpid() ) )
    
    def sigterm_handler(signo, frame):
        print('exit now')
        raise SystemExit(1)
    
    signal.signal(signal.SIGTERM, sigterm_handler)

    atexit.register(lambda: os.remove(pid_file))
    q = queue.Queue()
    sock = socket.socket()
    server_ip = '0.0.0.0'
    port = 3999

    try:
        sock.bind((server_ip, port))
    except:
        print('bind local socket err')
        raise SystemExit(1)
    else:    
        print('bind local socket success, port is', port)
        sock.listen(5)

        # 将标准输出定向到文件
        STDOUT = '/tmp/daemon_stdout'
        with open(STDOUT, 'ab+', 0) as fd:
            os.dup2(fd.fileno(), sys.stdout.fileno())

        threads = []
        for i in range(3):
            thread = threading.Thread(target=echo, args=(q,))
            threads.append(thread)
        for thread in threads:
            thread.daemon = True
            thread.start()
            print('start thread')

        while True:
            con,host = sock.accept()
            q.put( (con, host) )


def main():

    pid_file = '/tmp/pid.tmp'

    if len(sys.argv) == 2 and sys.argv[1] == 'start':
        if os.path.exists(pid_file):
            with open(pid_file) as fd:
                pid = fd.read()
            print('already running with pid', pid)
        else:
            echo_server()
    elif len(sys.argv) == 2 and sys.argv[1] == 'stop':
        if os.path.exists(pid_file):
            with open(pid_file) as fd:
                pid = fd.read()
                os.kill( int(pid), signal.SIGTERM )
                print('kill pid', pid)
        else:
            print('not running')
    else:
        print('usage:\n    python3 daemon.py start | stop')


if __name__ == '__main__':
    lock = threading.Lock()
    main()
