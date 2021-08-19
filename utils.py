import os
import sys
from sys import platform
from ast import *

################################################################################
# repr for classes in the ast module
################################################################################

def repr_Module(self):
    return '\n'.join([repr(s) for s in self.body])
Module.__repr__ = repr_Module

def repr_Expr(self):
    return repr(self.value)
Expr.__repr__ = repr_Expr

def repr_Assign(self):
    return repr(self.targets[0]) + ' = ' + repr(self.value)
Assign.__repr__ = repr_Assign

def repr_Return(self):
    return 'return ' + repr(self.value)
Return.__repr__ = repr_Return

def repr_Name(self):
    return self.id
Name.__repr__ = repr_Name

def repr_Constant(self):
    return repr(self.value)
Constant.__repr__ = repr_Constant

def repr_Add(self):
    return '+'
Add.__repr__ = repr_Add

def repr_And(self):
    return 'and'
And.__repr__ = repr_And

def repr_Or(self):
    return 'or'
Or.__repr__ = repr_Or

def repr_BinOp(self):
    return repr(self.left) + ' ' + repr(self.op) + ' ' + repr(self.right)
BinOp.__repr__ = repr_BinOp

def repr_BoolOp(self):
    return repr(self.values[0]) + ' ' + repr(self.op) + ' ' + repr(self.values[1])
BoolOp.__repr__ = repr_BoolOp

def repr_USub(self):
    return '-'
USub.__repr__ = repr_USub

def repr_Not(self):
    return 'not'
Not.__repr__ = repr_Not

def repr_UnaryOp(self):
    return repr(self.op) + ' ' + repr(self.operand)
UnaryOp.__repr__ = repr_UnaryOp

def repr_Call(self):
    return repr(self.func) \
        + '(' + ', '.join([repr(arg) for arg in self.args]) + ')'
Call.__repr__ = repr_Call

def repr_If(self):
    return 'if ' + repr(self.test) + ':\n' \
        + '\n'.join([repr(s) for s in self.body]) + '\n' \
        + 'else:\n' \
        + '\n'.join([repr(s) for s in self.orelse]) + '\n'
If.__repr__ = repr_If

def repr_IfExp(self):
    return '(' + repr(self.body) + ' if ' + repr(self.test) + \
        ' else ' + repr(self.orelse) + ')'
IfExp.__repr__ = repr_IfExp

def repr_Compare(self):
    return repr(self.left) + ' ' + repr(self.ops[0]) + ' ' + repr(self.comparators[0])
Compare.__repr__ = repr_Compare

def repr_Eq(self):
    return '=='
Eq.__repr__ = repr_Eq

def repr_Lt(self):
    return '<'
Lt.__repr__ = repr_Lt


################################################################################
# __eq__ and __hash__ for classes in the ast module
################################################################################

def eq_Name(self, other):
    if isinstance(other, Name):
        return self.id == other.id
    else:
        return False
Name.__eq__ = eq_Name

def hash_Name(self):
    return hash(self.id)
Name.__hash__ = hash_Name

################################################################################
# Generating unique names
################################################################################

name_id = 0

def generate_name(name):
    global name_id
    ls = name.split('_')
    new_id = name_id
    name_id += 1
    return ls[0] + "_" + str(new_id)


################################################################################
# AST classes
################################################################################

class Let(expr):
    __match_args__ = ("var", "rhs", "body")
    def __init__(self, var, rhs, body):
        self.var = var
        self.rhs = rhs
        self.body = body
    def __repr__(self):
        return 'let ' + repr(self.var) + ' = ' + repr(self.rhs) + ' in ' \
            + repr(self.body)

def make_lets(bs, e):
    result = e
    for (x,rhs) in reversed(bs):
        result = Let(x, rhs, result)
    return result

class CProgram:
    __match_args__ = ("body",)
    def __init__(self, body):
        self.body = body

    def __repr__(self):
        result = ''
        for (l,ss) in self.body.items():
            result += l + ':\n'
            result += '\n'.join([repr(s) for s in ss]) + '\n\n'
        return result
    
class Goto(expr):
    __match_args__ = ("label",)
    def __init__(self, label):
        self.label = label
    def __repr__(self):
        return 'goto ' + self.label

    
################################################################################
# Miscellaneous Auxiliary Functions
################################################################################

def input_int() -> int:
    return int(input())

def unzip(ls):
    xs,ys = [],[]
    for (x,y) in ls:
        xs += [x]
        ys += [y]
    return (xs,ys)

def align(n: int, alignment: int) -> int:
    if 0 == n % alignment:
        return n
    else:
        return n + (alignment - n % alignment)

def label_name(n: str) -> str:
    if platform == "darwin":
        return '_' + n
    else:
        return n
    
tracing = False

def trace(msg):
    if tracing:
        print(msg, file=sys.stderr)

def is_python_extension(filename):
    return filename.split(".")[1] == "py"

# Given the `ast` output of a pass and a test program (root) name,
# runs the interpreter on the program and compares the output to the
# expected "golden" output.
def test_pass(passname, interp, program_root, ast,
              compiler_name):
    if not interp:
        return 0
    input_file = program_root + '.in'
    output_file = program_root + '.out'
    stdin = sys.stdin
    stdout = sys.stdout
    sys.stdin = open(input_file, 'r')
    sys.stdout = open(output_file, 'w')
    interp(ast)
    sys.stdin = stdin
    sys.stdout = stdout
    os.system("sed -i '$a\\' " + program_root + '.out')
    os.system("sed -i '$a\\' " + program_root + '.golden')
    result = os.system('diff ' + output_file + ' ' + program_root + '.golden')
    if result == 0:
        trace('compiler ' + compiler_name + ' success on pass ' + passname \
              + ' on test\n' + program_root + '\n')
        return 1
    else:
        print('compiler ' + compiler_name + ' failed pass ' + passname \
              + ' on test\n' + program_root + '\n')
        return 0
        

def compile_and_test(compiler, compiler_name, type_check_P, interp_P, interp_C,
                     program_filename):
    total_passes = 0
    successful_passes = 0
    emulate_x86 = True
    if emulate_x86:
        from interp_x86.eval_x86 import interp_x86
    else:
        interp_x86 = None

    program_root = program_filename.split('.')[0]
    with open(program_filename) as source:
        program = parse(source.read())

    trace('\n**********\n type check \n**********\n')        
    type_check_P(program)
        
    if hasattr(compiler, 'shrink'):
        trace('\n**********\n shrink \n**********\n')
        program = compiler.shrink(program)
        trace(program)
        trace('')
        total_passes += 1
        successful_passes += \
            test_pass('shrink', interp_P, program_root, program, compiler_name)
        
    trace('\n**********\n remove \n**********\n')
    rco = compiler.remove_complex_operands(program)
    trace(rco)
    trace("")
    total_passes += 1
    successful_passes += \
        test_pass('remove complex operands', interp_P, program_root, rco,
                  compiler_name)
    
    if hasattr(compiler, 'explicate_control'):
        trace('\n**********\n explicate \n**********\n')
        rco = compiler.explicate_control(rco)
        trace(rco)
        total_passes += 1
        successful_passes += \
            test_pass('explicate control', interp_C, program_root, rco,
                      compiler_name)
        
    trace('\n**********\n select \n**********\n')    
    pseudo_x86 = compiler.select_instructions(rco)
    trace(pseudo_x86)
    trace("")
    total_passes += 1
    successful_passes += \
        test_pass('select instructions', interp_x86, program_root, pseudo_x86,
                  compiler_name)
    
    trace('\n**********\n assign \n**********\n')    
    almost_x86 = compiler.assign_homes(pseudo_x86)
    trace(almost_x86)
    trace("")
    total_passes += 1
    successful_passes += \
        test_pass('assign homes', interp_x86, program_root, almost_x86,
                  compiler_name)
    
    trace('\n**********\n patch \n**********\n')        
    x86 = compiler.patch_instructions(almost_x86)
    trace(x86)
    trace("")
    total_passes += 1
    successful_passes += \
        test_pass('patch instructions', interp_x86, program_root, x86,
                  compiler_name)

    trace('\n**********\n print x86 \n**********\n')            
    x86_filename = program_root + ".s"
    with open(x86_filename, "w") as dest:
        dest.write(compiler.print_x86(x86))

    x86 = compiler.generate_main(x86)
        
    total_passes += 1
        
    # Run the x86 program
    if emulate_x86:
        stdin = sys.stdin
        stdout = sys.stdout
        sys.stdin = open(program_root + '.in', 'r')
        sys.stdout = open(program_root + '.out', 'w')
        interp_x86(x86)
        sys.stdin = stdin
        sys.stdout = stdout
    else:
        os.system('gcc runtime.o ' + x86_filename)
        input_file = program_root + '.in'
        output_file = program_root + '.out'
        os.system('./a.out < ' + input_file + ' > ' + output_file)

    os.system("sed -i '$a\\' " + program_root + '.out')
    os.system("sed -i '$a\\' " + program_root + '.golden')
    result = os.system('diff ' + program_root + '.out ' \
                       + program_root + '.golden')
    if result == 0:
        successful_passes += 1
        return (successful_passes, total_passes, 1)
    else:
        print('compiler ' + compiler_name + ', executable failed' \
              + ' on test ' + program_root)
        return (successful_passes, total_passes, 0)


# Given a test file name, the name of a language, a compiler, a type
# checker and interpreter for the language, and an interpeter for the
# C intermediate language, run all the passes in the compiler,
# checking that the resulting programs produce output that matches the
# golden file.
def run_one_test(test, lang, compiler, compiler_name,
                 type_check_P, interp_P, interp_C):
    test_root = test.split('.')[0]
    test_name = test_root.split('/')[-1]
    return compile_and_test(compiler, compiler_name, type_check_P,
                            interp_P, interp_C, test)

# Given the name of a language, a compiler, the compiler's name, a
# type checker and interpreter for the language, and an interpreter
# for the C intermediate language, test the compiler on all the tests
# in the directory of for the given language, i.e., all the
# python files in ./tests/<language>.
def run_tests(lang, compiler, compiler_name, type_check_P, interp_P, interp_C):
    # Collect all the test programs for this language.
    homedir = os.getcwd()
    directory = homedir + '/tests/' + lang + '/'
    if not os.path.isdir(directory):
        raise Exception('missing directory for test programs: ' \
                        + directory)
    for (dirpath, dirnames, filenames) in os.walk(directory):
        tests = filter(is_python_extension, filenames)
        tests = [dirpath + t for t in tests]
        break
    # Compile and run each test program, comparing output to the golden file.
    successful_passes = 0
    total_passes = 0
    successful_tests = 0
    total_tests = 0
    for test in tests:
        (succ_passes, tot_passes, succ_test) = \
            run_one_test(test, lang, compiler, compiler_name,
                     type_check_P, interp_P, interp_C)
        successful_passes += succ_passes
        total_passes += tot_passes
        successful_tests += succ_test
        total_tests += 1

    # Report the pass/fails
    print('compiler ' + compiler_name + ' on language ' + lang \
          + ' passed ' + repr(successful_tests) + '/' + repr(total_tests) \
          + ' tests')
    print('compiler ' + compiler_name + ' on language ' + lang \
          + ' passed ' + repr(successful_passes) + '/' + repr(total_passes) \
          + ' passes')
