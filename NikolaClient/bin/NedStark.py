# -*- coding: utf8 -*-

import os
import sys
import platform
platform.system()


# from linux
if platform.system() == 'Windows':
    BASE_DIR = '\\'.join(os.path.abspath(os.path.dirname(__file__)).split('\\')[:-1])
    print (BASE_DIR)
else:
    BASE_DIR = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(BASE_DIR)


from core import HouseStark

if __name__ == '__main__':

    HouseStark.ArgvHandler(sys.argv)