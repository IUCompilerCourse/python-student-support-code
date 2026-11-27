import os
import sys
from sys import platform
import ast
from ast import parse

sys.path.append('../python-student-support-code')
sys.path.append('../python-student-support-code/interp_x86')

import compiler
from interp_Lvar import interp_Lvar
from interp_x86.eval_x86 import interp_x86
from utils import is_python_extension

# The interp_and_check function runs the interpreter on the program
# AST and compares the output to the expected output in the golden file.
def interp_and_check(program_filename, program_ast, interpreter, passname):
  # redirect standard input and output
  program_root = os.path.splitext(program_filename)[0]
  input_file = program_root + '.in'
  output_file = program_root + '.out'
  stdin = sys.stdin
  stdout = sys.stdout
  sys.stdin = open(input_file, 'r')
  sys.stdout = open(output_file, 'w')
  # run the program!  
  interpreter(program_ast)
  print() # print a newline to make diff happy
  # reset standard input and output
  sys.stdin = stdin
  sys.stdout = stdout
  # compare the output to the expected "golden" result
  result = os.system('diff' + ' -b ' + output_file \
                     + ' ' + program_root + '.golden')
  if result == 0:
    print(passname + ': passed')
  else:
    print(passname + ': error')

# The execute_and_check function prints the AST to an assembly file,
# uses gcc to compile it into an executable, runs the executable,
# and compares the output to the expected output in the golden file.
def execute_and_check(program_filename, program_ast):
  program_root = os.path.splitext(program_filename)[0]

  # Write the assembly file
  x86_filename = program_root + ".s"
  with open(x86_filename, "w") as dest:
      dest.write(str(program_ast))

  # Create the executable, linking with the runtime
  if platform == 'darwin':
      os.system('gcc -arch x86_64 runtime.o ' + x86_filename)
  else:
      os.system('gcc runtime.o ' + x86_filename)
      
  input_file = program_root + '.in'
  output_file = program_root + '.out'
  os.system('./a.out < ' + input_file + ' > ' + output_file)
  result = os.system('diff' + ' -b ' + program_root + '.out ' \
                     + program_root + '.golden')
  if result == 0:
      print('executable passed')
  else:
      print('executable failed')
      
  
if __name__ == "__main__":
  # Create a compiler object.
  C = compiler.Compiler()

  all_tests = False
  
  # Collect the test programs from the /tests/var subdirectory.
  if all_tests:
    lang = 'var'
    homedir = os.getcwd()
    directory = homedir + '/tests/' + lang + '/'
    for (dirpath, dirnames, filenames) in os.walk(directory):
      tests = [dirpath + t for t in filter(is_python_extension, filenames)]
      break
  else:
      tests = [os.getcwd() + '/tests/var/' + 'sub-input-flat.py']
      
  # Evaluate the compiler on each test program.
  for program_filename in tests:
    print('testing ' + os.path.basename(program_filename))
    
    # Parse the input program
    with open(program_filename) as source:
        program_ast = parse(source.read())

    print('Program Concrete Syntax:')
    print(program_ast)
    print('Program Abstract Syntax:')
    print(repr(program_ast))
    print()
        
    # Remove Complex Operands
    program_ast = C.remove_complex_operands(program_ast)
    print('After RCO')
    print('Concrete Syntax:')
    print(program_ast)
    print('Abstract Syntax:')
    print(repr(program_ast))
    interp_and_check(program_filename, program_ast,
                    interp_Lvar, 'remove complex operands')
    print()
      
    if False:
      # Move up each pass once it is completed 
      

      # Select Instructions
      program_ast = C.select_instructions(program_ast)
      interp_and_check(program_filename, program_ast,
                       interp_x86, 'select instructions')

      # Assign Homes
      program_ast = C.assign_homes(program_ast)
      interp_and_check(program_filename, program_ast,
                       interp_x86, 'assign homes')

      # Patch Instruction 
      program_ast = C.patch_instructions(program_ast)
      interp_and_check(program_filename, program_ast,
                       interp_x86, 'patch instructions')

      # Prelude and Conclusion
      program_ast = C.prelude_and_conclusion(program_ast)
      execute_and_check(program_filename, program_ast)

      print()




