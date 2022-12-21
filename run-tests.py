import os
import compiler
from utils import run_tests, run_one_test

compiler = compiler.Compiler()

if False:
    run_one_test(os.getcwd() + '/tests/var/zero.py',
                 compiler)
else:
    run_tests('var', compiler)
