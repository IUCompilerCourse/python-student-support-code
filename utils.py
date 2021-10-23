import os
import sys
from sys import platform
from ast import *

################################################################################
# repr for classes in the ast module
################################################################################

indent_amount = 0

def indent_stmt():
    return " " * indent_amount

def indent():
    global indent_amount
    indent_amount += 2

def dedent():
    global indent_amount
    indent_amount -= 2

def str_Module(self):
    indent()
    body = ''.join([str(s) for s in self.body])
    dedent()
    return body
Module.__str__ = str_Module
def repr_Module(self):
    return 'Module(' + repr(self.body) + ')'
Module.__repr__ = repr_Module

def str_Expr(self):
    return indent_stmt() + str(self.value) + '\n'
Expr.__str__ = str_Expr
def repr_Expr(self):
    return indent_stmt() + 'Expr(' + repr(self.value) + ')'
Expr.__repr__ = repr_Expr

def str_Assign(self):
    return indent_stmt() + str(self.targets[0]) + ' = ' + str(self.value) + '\n'
Assign.__str__ = str_Assign
def repr_Assign(self):
    return indent_stmt() + 'Assign(' + repr(self.targets) + ', ' + repr(self.value) + ')'
Assign.__repr__ = repr_Assign

def str_Return(self):
    return indent_stmt() + 'return ' + str(self.value) + '\n'
Return.__str__ = str_Return
def repr_Return(self):
    return indent_stmt() + 'Return(' + repr(self.value) + ')'
Return.__repr__ = repr_Return

def str_Name(self):
    return self.id
Name.__str__ = str_Name
def repr_Name(self):
    return 'Name(' + repr(self.id) + ')'
Name.__repr__ = repr_Name

def str_Constant(self):
    return str(self.value)
Constant.__str__ = str_Constant
def repr_Constant(self):
    return 'Constant(' + repr(self.value) + ')'
Constant.__repr__ = repr_Constant

def str_Add(self):
    return '+'
Add.__str__ = str_Add
def repr_Add(self):
    return 'Add()'
Add.__repr__ = repr_Add

def str_Sub(self):
    return '-'
Sub.__str__ = str_Sub
def repr_Sub(self):
    return 'Sub()'
Sub.__repr__ = repr_Sub

def str_And(self):
    return 'and'
And.__str__ = str_And
def repr_And(self):
    return 'And()'
And.__repr__ = repr_And

def str_Or(self):
    return 'or'
Or.__str__ = str_Or
def repr_Or(self):
    return 'Or()'
Or.__repr__ = repr_Or

def str_BinOp(self):
    return str(self.left) + ' ' + str(self.op) + ' ' + str(self.right)
BinOp.__str__ = str_BinOp
def repr_BinOp(self):
    return 'BinOp(' + repr(self.left) + ', ' + repr(self.op) + ', ' + repr(self.right) + ')'
BinOp.__repr__ = repr_BinOp

def str_BoolOp(self):
    return str(self.values[0]) + ' ' + str(self.op) + ' ' + str(self.values[1])
BoolOp.__str__ = str_BoolOp
def repr_BoolOp(self):
    return repr(self.values[0]) + ' ' + repr(self.op) + ' ' + repr(self.values[1])
BoolOp.__repr__ = repr_BoolOp

def str_USub(self):
    return '-'
USub.__str__ = str_USub
def repr_USub(self):
    return 'USub()'
USub.__repr__ = repr_USub

def str_Not(self):
    return 'not'
Not.__str__ = str_Not
def repr_Not(self):
    return 'Not()'
Not.__repr__ = repr_Not

def str_UnaryOp(self):
    return str(self.op) + ' ' + str(self.operand)
UnaryOp.__str__ = str_UnaryOp
def repr_UnaryOp(self):
    return 'UnaryOp(' + repr(self.op) + ', ' + repr(self.operand) + ')'
UnaryOp.__repr__ = repr_UnaryOp

def str_Call(self):
    return str(self.func) \
        + '(' + ', '.join([str(arg) for arg in self.args]) + ')'
Call.__str__ = str_Call
def repr_Call(self):
    return 'Call(' + repr(self.func) + ', ' + repr(self.args) + ')'
Call.__repr__ = repr_Call

def str_If(self):
    header = indent_stmt() + 'if ' + str(self.test) + ':\n'
    indent()
    thn = ''.join([str(s) for s in self.body])
    els = ''.join([str(s) for s in self.orelse])
    dedent()
    return header  + thn + indent_stmt() + 'else:\n' + els
If.__str__ = str_If
def repr_If(self):
    return 'If(' + repr(self.test) + ', ' + repr(self.body) + ', ' + repr(self.orelse) + ')'
If.__repr__ = repr_If

def str_IfExp(self):
    return '(' + str(self.body) + ' if ' + str(self.test) + \
        ' else ' + str(self.orelse) + ')'
IfExp.__str__ = str_IfExp
def repr_IfExp(self):
    return 'IfExp(' + repr(self.body) + ', ' + repr(self.test) + ', ' + repr(self.orelse) + ')'
IfExp.__repr__ = repr_IfExp

def str_While(self):
    header = indent_stmt() + 'while ' + str(self.test) + ':\n'
    indent()
    body = ''.join([str(s) for s in self.body])
    dedent()
    return header + body
While.__str__ = str_While
def repr_While(self):
    return 'While(' + repr(self.test) + ', ' + repr(self.body) + ', ' + repr(self.orelse) + ')'
While.__repr__ = repr_While

def str_Compare(self):
    return str(self.left) + ' ' + str(self.ops[0]) + ' ' + str(self.comparators[0])
Compare.__str__ = str_Compare
def repr_Compare(self):
    return 'Compare(' + repr(self.left) + ', ' + repr(self.ops) + ', ' \
        + repr(self.comparators) + ')'
Compare.__repr__ = repr_Compare

def str_Eq(self):
    return '=='
Eq.__str__ = str_Eq
def repr_Eq(self):
    return 'Eq()'
Eq.__repr__ = repr_Eq

def str_NotEq(self):
    return '!='
NotEq.__str__ = str_NotEq
def repr_NotEq(self):
    return 'NotEq()'
NotEq.__repr__ = repr_NotEq

def str_Lt(self):
    return '<'
Lt.__str__ = str_Lt
def repr_Lt(self):
    return 'Lt()'
Lt.__repr__ = repr_Lt

def str_LtE(self):
    return '<='
LtE.__str__ = str_Lt
def repr_LtE(self):
    return 'LtE()'
LtE.__repr__ = repr_LtE

def str_Gt(self):
    return '>'
Gt.__str__ = str_Gt
def repr_Gt(self):
    return 'Gt()'
Gt.__repr__ = repr_Gt

def str_GtE(self):
    return '>='
GtE.__str__ = str_GtE
def repr_GtE(self):
    return 'GtE()'
GtE.__repr__ = repr_GtE

def str_Tuple(self):
    return '(' + ','.join([str(e) for e in self.elts])  + ',)'
Tuple.__str__ = str_Tuple
def repr_Tuple(self):
    return 'Tuple(' + repr(self.elts) + ')'
Tuple.__repr__ = repr_Tuple

def str_Subscript(self):
    return str(self.value) + '[' + str(self.slice) + ']'
Subscript.__str__ = str_Subscript
def repr_Subscript(self):
    return 'Subscript(' + repr(self.value) + ', ' + repr(self.slice) + ')'
Subscript.__repr__ = repr_Subscript


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
    ls = name.split('.')
    new_id = name_id
    name_id += 1
    return ls[0] + '.' + str(new_id)


################################################################################
# AST classes
################################################################################

class Let(expr):
    __match_args__ = ("var", "rhs", "body")
    def __init__(self, var, rhs, body):
        self.var = var
        self.rhs = rhs
        self.body = body
    def __str__(self):
        return '(let ' + str(self.var) + ' = ' + str(self.rhs) + ' in ' \
            + str(self.body) + ')'
    def __repr__(self):
        return 'Let(' + repr(self.var) + ',' + repr(self.rhs) + ',' \
            + repr(self.body) + ')'

def make_lets(bs, e):
    result = e
    for (x,rhs) in reversed(bs):
        result = Let(x, rhs, result)
    return result

class CProgram:
    __match_args__ = ("body",)
    def __init__(self, body):
        self.body = body

    def __str__(self):
        result = ''
        for (l,ss) in self.body.items():
            result += l + ':\n'
            indent()
            result += ''.join([str(s) for s in ss]) + '\n'
            dedent()
        return result

    def __repr__(self):
        return 'CProgram(' + repr(self.body) + ')'
    
class Goto(stmt):
    __match_args__ = ("label",)
    def __init__(self, label):
        self.label = label
    def __str__(self):
        return indent_stmt() + 'goto ' + self.label + '\n'
    def __repr__(self):
        return 'Goto(' + repr(self.label) + ')'

class Allocate(expr):
    __match_args__ = ("length", "ty")
    def __init__(self, length, ty):
        self.length = length
        self.ty = ty
    def __str__(self):
        return 'allocate(' + str(self.length) + ',' + str(self.ty) + ')'
    def __repr__(self):
        return 'Allocate(' + repr(self.length) + ',' + repr(self.ty) + ')'

class Collect(stmt):
    __match_args__ = ("size",)
    def __init__(self, size):
        self.size = size
    def __str__(self):
        return indent_stmt() + 'collect(' + str(self.size) + ')\n'
    def __repr__(self):
        return 'Collect(' + repr(self.size) + ')'
    
class Begin(expr):
    __match_args__ = ("body", "result")
    def __init__(self, body, result):
        self.body = body
        self.result = result
    def __str__(self):
        indent()
        stmts = ''.join([str(s) for s in self.body])
        end = indent_stmt() + str(self.result)
        dedent()
        return 'begin:\n' + stmts + end
    def __repr__(self):
        return 'Begin(' + repr(self.body) + ',' + repr(self.result) + ')'

class GlobalValue(expr):
    __match_args__ = ("name",)
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return str(self.name)
    def __repr__(self):
        return 'GlobalValue(' + repr(self.name) + ')'

class TupleType:
    __match_args__ = ("types",)
    def __init__(self, types):
        self.types = types
    def __str__(self):
        return 'tuple' + str(self.types)
    def __repr__(self):
        return 'TupleType(' + repr(self.types) + ')'
    
        
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

def bool2int(b):
    if b:
        return 1
    else:
        return 0
    
def label_name(n: str) -> str:
    if platform == "darwin":
        return '_' + n
    else:
        return n
    
tracing = False

def enable_tracing():
    global tracing
    tracing = True

def trace(msg):
    if tracing:
        print(msg, file=sys.stderr)

def is_python_extension(filename):
    s = filename.split(".")
    if len(s) > 1:
        return s[1] == "py"
    else:
        return False

# Given the `ast` output of a pass and a test program (root) name,
# runs the interpreter on the program and compares the output to the
# expected "golden" output.
def test_pass(passname, interp, program_root, ast,
              compiler_name):
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
    from interp_x86.eval_x86 import interp_x86

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
        
    if hasattr(compiler, 'expose_allocation'):
        trace('\n**********\n expose allocation \n**********\n')
        type_check_P(program)
        program = compiler.expose_allocation(program)
        trace(program)
        total_passes += 1
        successful_passes += \
            test_pass('expose allocation', interp_P, program_root, program,
                      compiler_name)
        
    trace('\n**********\n remove \n**********\n')
    program = compiler.remove_complex_operands(program)
    trace(program)
    trace("")
    total_passes += 1
    successful_passes += \
        test_pass('remove complex operands', interp_P, program_root, program,
                  compiler_name)
    
    if hasattr(compiler, 'explicate_control'):
        trace('\n**********\n explicate \n**********\n')
        program = compiler.explicate_control(program)
        trace(program)
        total_passes += 1
        successful_passes += \
            test_pass('explicate control', interp_C, program_root, program,
                      compiler_name)
        
    trace('\n**********\n select \n**********\n')    
    pseudo_x86 = compiler.select_instructions(program)
    trace(pseudo_x86)
    trace("")
    total_passes += 1
    test_x86 = False
    if test_x86:
        successful_passes += \
            test_pass('select instructions', interp_x86, program_root, pseudo_x86,
                      compiler_name)
    
    trace('\n**********\n assign \n**********\n')    
    almost_x86 = compiler.assign_homes(pseudo_x86)
    trace(almost_x86)
    trace("")
    total_passes += 1
    if test_x86:    
        successful_passes += \
            test_pass('assign homes', interp_x86, program_root, almost_x86,
                      compiler_name)
    
    trace('\n**********\n patch \n**********\n')        
    x86 = compiler.patch_instructions(almost_x86)
    trace(x86)
    trace("")
    total_passes += 1
    if test_x86:    
        successful_passes += \
            test_pass('patch instructions', interp_x86, program_root, x86,
                      compiler_name)

    trace('\n**********\n prelude and conclusion \n**********\n')
    x86 = compiler.prelude_and_conclusion(x86)
    trace(x86)
    trace("")
    
    x86_filename = program_root + ".s"
    with open(x86_filename, "w") as dest:
        dest.write(str(x86))
        
    total_passes += 1
        
    # Run the final x86 program
    emulate_x86 = False
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

def trace_ast_and_concrete(ast):
    trace("concrete syntax:")
    trace(ast)
    trace("")
    trace("AST:")
    trace(repr(ast))    
    
# This function compiles the program without any testing
def compile(compiler, compiler_name, type_check_P, program_filename):
    program_root = program_filename.split('.')[0]
    with open(program_filename) as source:
        program = parse(source.read())

    trace('\n**********\n type check \n**********\n')        
    type_check_P(program)
    trace_ast_and_concrete(program)
        
    if hasattr(compiler, 'shrink'):
        trace('\n**********\n shrink \n**********\n')
        program = compiler.shrink(program)
        trace_ast_and_concrete(program)
        
    trace('\n**********\n remove \n**********\n')
    program = compiler.remove_complex_operands(program)
    trace_ast_and_concrete(program)
    
    if hasattr(compiler, 'explicate_control'):
        trace('\n**********\n explicate \n**********\n')
        program = compiler.explicate_control(program)
        trace_ast_and_concrete(program)
        
    trace('\n**********\n select \n**********\n')    
    pseudo_x86 = compiler.select_instructions(program)
    trace_ast_and_concrete(pseudo_x86)
    
    trace('\n**********\n assign \n**********\n')    
    almost_x86 = compiler.assign_homes(pseudo_x86)
    trace_ast_and_concrete(almost_x86)
    
    trace('\n**********\n patch \n**********\n')        
    x86 = compiler.patch_instructions(almost_x86)
    trace_ast_and_concrete(x86)

    trace('\n**********\n prelude and conclusion \n**********\n')
    x86 = compiler.prelude_and_conclusion(x86)
    trace_ast_and_concrete(x86)
    
    # Output x86 program to the .s file
    x86_filename = program_root + ".s"
    with open(x86_filename, "w") as dest:
        dest.write(str(x86))        
    

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
    print('tests: ' + repr(successful_tests) + '/' + repr(total_tests) \
          + ' for compiler ' + compiler_name + ' on language ' + lang)
    print('passes: ' + repr(successful_passes) + '/' + repr(total_passes) \
          + ' for compiler ' + compiler_name + ' on language ' + lang)
