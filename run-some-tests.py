#!/usr/bin/env python3
import os
import sys
import getopt

from utils import run_selected_tests, enable_tracing, enable_emulation

import var

sys.setrecursionlimit(10000)

try:
    opts, files = getopt.getopt(sys.argv[1:],"te")
except getopt.GetoptError:
    print ('usage: run-tests.py [-t] [-e]')
    sys.exit(1)

for opt,arg  in opts:
    if opt == '-t':
        enable_tracing()
    if opt == '-e':
        enable_emulation()
        
run_selected_tests(files,
                   var.Var(), 'var',
                   var.type_check_dict, var.interp_dict) 

