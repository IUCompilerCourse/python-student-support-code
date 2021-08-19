import os
import compiler
import interp_Pvar
import type_check_Pvar
from utils import run_tests, run_one_test

compiler = compiler.Compiler()
if False:
    run_one_test(os.getcwd() + '/tests/var/zero.py', 'var',
                 compiler, 'var',
                 type_check_Pvar.TypeCheckPvar().type_check_P,
                 interp_Pvar.InterpPvar().interp_P,
                 None)
else:
    run_tests('var', compiler, 'var',
              type_check_Pvar.TypeCheckPvar().type_check_P,
              interp_Pvar.InterpPvar().interp_P,
              None)

