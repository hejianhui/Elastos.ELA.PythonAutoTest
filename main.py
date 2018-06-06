import subprocess
import time
import os
import importlib
import sys
from account import account


def main():
    cases_dir = './'
    cases = list()
    files = os.listdir(cases_dir)
    for case in files:
        if case.endswith('_test.py'):
            cases.append(case)

    for case in cases:
        print('cases now is:', case)
        a = subprocess.Popen('python3 ' + case, cwd=cases_dir, shell=True)
        while True:
            result = a.poll()
            time.sleep(0.1)
            if result is not None:
                print('terminate a')
                a.terminate()
                break


if __name__ == '__main__':
    main()
