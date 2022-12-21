import os
import sys
from sys import platform
import ast
from ast import *
from dataclasses import dataclass
from contextlib import redirect_stdout,_RedirectStream

# move these to the compilers, use a method with overrides -Jeremy
builtin_functions = \
    {'input_int', 'print',
     'arity',
     'len',
     'array_len', 'array_load', 'array_store',
     'any_load', 'any_load_unsafe', 'any_store', 'any_store_unsafe',
     'any_len', 'make_any',
     'exit',
     'is_tuple_proxy', 'project_tuple', 'proxy_tuple_load', 'proxy_tuple_len',
     'is_array_proxy', 'project_array', 'proxy_array_load', 'proxy_array_len',
     'proxy_array_store',
     }

tag_is_array_right_shift = 62
tag_is_proxy_right_shift = 63

################################################################################
# repr for classes in the ast module
################################################################################

indent_amount = 2


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


def str_Pass(self):
    return indent_stmt() + 'pass\n'


Pass.__str__ = str_Pass


def repr_Pass(self):
    return indent_stmt() + 'Pass()'


Pass.__repr__ = repr_Pass


def str_Assign(self):
    return indent_stmt() + str(self.targets[0]) + ' = ' + str(self.value) + '\n'


Assign.__str__ = str_Assign


def repr_Assign(self):
    return indent_stmt() + 'Assign(' + repr(self.targets) + ', ' + repr(self.value) + ')'


Assign.__repr__ = repr_Assign


def str_AnnAssign(self):
    return indent_stmt() + str(self.target) + ' : ' + str(self.annotation) + ' = ' + str(self.value) + '\n'


AnnAssign.__str__ = str_AnnAssign


def repr_AnnAssign(self):
    return indent_stmt() + 'AnnAssign(' + repr(self.target) + ', ' \
           + repr(self.annotation) + ', ' + repr(self.value) + ')'


AnnAssign.__repr__ = repr_AnnAssign


def str_Return(self):
    return indent_stmt() + 'return ' + str(self.value) + '\n'


Return.__str__ = str_Return


def repr_Return(self):
    return indent_stmt() + 'Return(' + repr(self.value) + ')'


Return.__repr__ = repr_Return


def str_Name(self):
    if hasattr(self, 'has_type'):
        return self.id + ':' + str(self.has_type)
    else:
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


def str_Mult(self):
    return '*'


Mult.__str__ = str_Mult


def repr_Mult(self):
    return 'Mult()'


Mult.__repr__ = repr_Mult


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
    return '(' + str(self.left) + ' ' + str(self.op) + ' ' + str(self.right) + ')'


BinOp.__str__ = str_BinOp


def repr_BinOp(self):
    return 'BinOp(' + repr(self.left) + ', ' + repr(self.op) + ', ' + repr(self.right) + ')'


BinOp.__repr__ = repr_BinOp


def str_BoolOp(self):
    return '(' + str(self.values[0]) + ' ' + str(self.op) + ' ' + str(self.values[1]) + ')'


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
    return str(self.op) + '(' + str(self.operand) + ')'


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
    return header + thn + indent_stmt() + 'else:\n' + els


If.__str__ = str_If


def repr_If(self):
    return 'If(' + repr(self.test) + ', ' + repr(self.body) + ', ' + repr(self.orelse) + ')'


If.__repr__ = repr_If


def str_IfExp(self):
    return '(' + str(self.body) + ' if ' + str(self.test) + \
           ' else ' + str(self.orelse) + ')'


IfExp.__str__ = str_IfExp


def repr_IfExp(self):
    return 'IfExp(' + repr(self.test) + ', ' + repr(self.body) + \
        ', ' + repr(self.orelse) + ')'


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


def str_Is(self):
    return 'is'


Is.__str__ = str_Is


def repr_Is(self):
    return 'Is()'


Is.__repr__ = repr_Is


def str_Tuple(self):
    return '(' + ', '.join([str(e) for e in self.elts]) + ',)'


Tuple.__str__ = str_Tuple


def repr_Tuple(self):
    return 'Tuple(' + repr(self.elts) + ')'


Tuple.__repr__ = repr_Tuple


def str_List(self):
    return '[' + ', '.join([str(e) for e in self.elts]) + ']'


ast.List.__str__ = str_List


def repr_List(self):
    return 'List(' + repr(self.elts) + ')'


ast.List.__repr__ = repr_List


def str_Subscript(self):
    return str(self.value) + '[' + str(self.slice) + ']'


Subscript.__str__ = str_Subscript


def repr_Subscript(self):
    return 'Subscript(' + repr(self.value) + ', ' + repr(self.slice) \
           + ', ' + repr(self.ctx) + ')'


Subscript.__repr__ = repr_Subscript


def str_FunctionDef(self):
    if isinstance(self.args, ast.arguments):
        params = ', '.join([a.arg + ' : ' + str(a.annotation) for a in self.args.args])
    else:
        params = ', '.join([x + ' : ' + str(t) for (x, t) in self.args])
    indent()
    if isinstance(self.body, list):
        body = ''.join([str(s) for s in self.body])
    elif isinstance(self.body, dict):
        body = ''
        for (l, ss) in self.body.items():
            body += l + ':\n'
            indent()
            body += ''.join([str(s) for s in ss])
            dedent()
    else:
        body = ''
    dedent()
    return indent_stmt() + 'def ' + self.name + '(' + params + ')' + \
           ' -> ' + str(self.returns) + ':\n' + body + '\n'


def repr_FunctionDef(self):
    return 'FunctionDef(' + self.name + ',' + repr(self.args) + ',' + \
           repr(self.body) + ')'


FunctionDef.__str__ = str_FunctionDef
FunctionDef.__repr__ = repr_FunctionDef


def str_Lambda(self):
    if isinstance(self.args, ast.arguments):
        params = ', '.join([a.arg for a in self.args.args])
    else:
        params = ', '.join([x for x in self.args])
    body = str(self.body)
    return '(lambda ' + params + ': ' + body + ')'


def repr_Lambda(self):
    return 'Lambda(' + repr(self.args) + ',' + repr(self.body) + ')'


Lambda.__str__ = str_Lambda
Lambda.__repr__ = repr_Lambda


def str_ImportFrom(self):
    return indent_stmt() + 'from' + ' X ' + 'import' + ' Y\n'

def repr_ImportFrom(self):
    return 'ImportFrom()'

ImportFrom.__str__ = str_ImportFrom
ImportFrom.__repr__ = repr_ImportFrom


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

class Type:
    pass

def make_assigns(bs):
    return [Assign([x], rhs) for (x, rhs) in bs]


def make_begin(bs, e):
    if len(bs) > 0:
        return Begin([Assign([x], rhs) for (x, rhs) in bs], e)
    else:
        return e


@dataclass
class Cast(expr):
    body: expr
    source: Type
    target: Type
    __match_args__ = ("body", "source", "target")

    def __str__(self):
        return '(' + str(self.body) + ' : ' + str(self.source) + ' => ' + str(self.target) + ')'


# A lambda expression whose parameters are annotated with types.
@dataclass
class AnnLambda(expr):
    params: list[tuple[str, Type]]
    returns: Type
    body: expr
    __match_args__ = ("params", "returns", "body")

    def __str__(self):
        return 'lambda [' + \
               ', '.join([x + ':' + str(t) for (x, t) in self.params]) + '] -> ' \
               + str(self.returns) + ': ' + str(self.body)


# Instantiate a generic function
@dataclass
class Inst(expr):
    generic: expr
    type_args: dict[str, Type]
    __match_args__ = ("generic", "type_args")

    def __str__(self):
        return str(self.generic) + str(self.type_args)
    
# An uninitialized value of a given type.
# Needed for boxing local variables.
@dataclass
class Uninitialized(expr):
    ty: Type
    __match_args__ = ("ty",)

    def __str__(self):
        return 'uninit[' + str(self.ty) + ']'


@dataclass
class CProgram:
    __match_args__ = ("body",)
    body: list[stmt]

    def __str__(self):
        result = ''
        for (l, ss) in self.body.items():
            result += l + ':\n'
            indent()
            result += ''.join([str(s) for s in ss]) + '\n'
            dedent()
        return result


@dataclass
class CProgramDefs:
    defs: list[stmt]
    __match_args__ = ("defs",)

    def __str__(self):
        return '\n'.join([str(d) for d in self.defs]) + '\n'


@dataclass
class Goto(stmt):
    label: str
    __match_args__ = ("label",)

    def __str__(self):
        return indent_stmt() + 'goto ' + self.label + '\n'


@dataclass
class Allocate(expr):
    length: int
    ty: Type
    __match_args__ = ("length", "ty")

    def __str__(self):
        return 'allocate(' + str(self.length) + ',' + str(self.ty) + ')'


@dataclass
class AllocateArray(expr):
    length: int
    ty: Type
    __match_args__ = ("length", "ty")

    def __str__(self):
        return 'allocate_array(' + str(self.length) + ',' + str(self.ty) + ')'


@dataclass
class AllocateClosure(expr):
    length: int
    ty: Type
    arity: int
    __match_args__ = ("length", "ty", "arity")

    def __str__(self):
        return 'alloc_clos(' + str(self.length) + ',' + str(self.ty) \
               + ',' + str(self.arity) + ')'


@dataclass
class Collect(stmt):
    size: int
    __match_args__ = ("size",)

    def __str__(self):
        return indent_stmt() + 'collect(' + str(self.size) + ')\n'


@dataclass
class Begin(expr):
    __match_args__ = ("body", "result")
    body: list[stmt]
    result: expr

    def __str__(self):
        indent()
        stmts = ''.join([str(s) for s in self.body])
        end = indent_stmt() + 'produce ' + str(self.result)
        dedent()
        return '{\n' + stmts + end + '}'


@dataclass
class GlobalValue(expr):
    name: str
    __match_args__ = ("name",)

    def __str__(self):
        return str(self.name)


@dataclass(eq=True)
class IntType(Type):
    def __str__(self):
        return 'int'


@dataclass(eq=True)
class BoolType(Type):
    def __str__(self):
        return 'bool'


@dataclass(eq=True)
class VoidType(Type):
    def __str__(self):
        return 'void'


@dataclass(eq=True)
class Bottom(Type):
    def __str__(self):
        return 'bottom'


@dataclass(eq=True)
class TupleType(Type):
    types: list[Type]
    __match_args__ = ("types",)

    def __str__(self):
        return 'tuple[' + ','.join([str(p) for p in self.types]) + ']'


@dataclass(eq=True)
class ListType(Type):
    elt_type: Type
    __match_args__ = ("elt_type",)

    def __str__(self):
        return 'list[' + str(self.elt_type) + ']'


@dataclass(eq=True)
class FunctionType:
    param_types: list[Type]
    ret_type: Type
    __match_args__ = ("param_types", "ret_type")

    def __str__(self):
        return 'Callable[[' + ','.join([str(p) for p in self.param_types]) + ']' \
               + ', ' + str(self.ret_type) + ']'

@dataclass(eq=True)
class GenericVar:
    id: str
    __match_args__ = ("id",)
    def __str__(self):
        return str(self.id)
    
@dataclass(eq=True)
class AllType:
    params: list[str]
    typ: Type
    __match_args__ = ("params", "typ")

    def __str__(self):
        return '∀ ' + ','.join([str(p) for p in self.params]) + '(' \
            + str(self.typ) + ')'

@dataclass(eq=True)
class FunRef(expr):
    name: str
    arity: int
    __match_args__ = ("name", "arity")

    def __str__(self):
        return '{' + self.name + '}'


@dataclass
class TailCall(stmt):
    func: expr
    args: list[expr]
    __match_args__ = ("func", "args")

    def __str__(self):
        return indent_stmt() + 'tail ' + str(self.func) + '(' + ', '.join([str(e) for e in self.args]) + ')\n'


# like a Tuple, but also stores the function's arity
@dataclass
class Closure(expr):
    arity: int
    args: list[expr]
    __match_args__ = ("arity", "args")

    def __str__(self):
        return 'closure{' + repr(self.arity) + '}(' + ', '.join([str(e) for e in self.args]) + ')'


@dataclass
class Inject(expr):
    value: expr
    typ: Type
    __match_args__ = ("value", "typ")

    def __str__(self):
        return 'inject(' + str(self.value) + ', ' + str(self.typ) + ')'


@dataclass
class Project(expr):
    value: expr
    typ: Type
    __match_args__ = ("value", "typ")

    def __str__(self):
        return 'project(' + str(self.value) + ', ' + str(self.typ) + ')'


@dataclass
class TagOf(expr):
    value: expr
    __match_args__ = ("value",)

    def __str__(self):
        return 'tagof(' + str(self.value) + ')'


@dataclass
class ValueOf(expr):
    value: expr
    typ: Type
    __match_args__ = ("value", "typ")

    def __str__(self):
        return 'valueof(' + str(self.value) + ', ' + str(self.typ) + ')'


@dataclass(eq=True)
class AnyType(Type):
    def __str__(self):
        return 'Any'


@dataclass(eq=True)
class ProxyOrTupleType(Type):
    elt_types: list[Type]

    def __str__(self):
        return 'POrTuple[' + ','.join([str(t) for t in self.elt_types]) + ']'


@dataclass(eq=True)
class ProxyOrListType(Type):
    elt_type: Type

    def __str__(self):
        return 'POrList[' + str(self.elt_type) + ']'


@dataclass(eq=True)
class TupleProxy(expr):
    value: expr
    reads: list[expr]
    source: Type
    target: Type

    def __str__(self):
        return 'tuple_proxy(' + str(self.value) + ', ' + str(self.source) \
               + ', ' + str(self.target) + ')'


@dataclass(eq=True)
class RawTuple(expr):
    elts: list[expr]

    def __str__(self):
        return '[[' + ','.join([str(e) for e in self.elts]) + ']]'


@dataclass(eq=True)
class ListProxy(expr):
    value: expr
    read: expr
    write: expr
    source: Type
    target: Type

    def __str__(self):
        return 'array_proxy(' + str(self.value) + ', ' + str(self.source) \
               + ', ' + str(self.target) + ')'


@dataclass(eq=True)
class InjectTuple(expr):
    value: expr

    def __str__(self):
        return 'inject_tuple[' + str(self.value) + ']'


@dataclass(eq=True)
class InjectTupleProxy(expr):
    value: expr
    typ: Type

    def __str__(self):
        return 'inject_tuple_proxy[' + str(self.value) + ' from ' + str(self.typ) + ']'


@dataclass(eq=True)
class InjectList(expr):
    value: expr

    def __str__(self):
        return 'inject_array[' + str(self.value) + ']'


@dataclass(eq=True)
class InjectListProxy(expr):
    value: expr
    typ: Type

    def __str__(self):
        return 'inject_array_proxy[' + str(self.value) + ' from ' + str(self.typ) + ']'


# Base class of runtime values
class Value:
    pass


# smuggle a runtime value back into the AST
@dataclass(eq=True)
class ValueExp(expr):
    value: Value


@dataclass(eq=True)
class ProxiedTuple(Value):
    tup: Value
    reads: list[Value]

    def __str__(self):
        return 'proxy[' + str(self.value) + ']'


@dataclass(eq=True)
class ProxiedList(Value):
    tup: Value
    read: Value
    write: Value

    def __str__(self):
        return 'proxy[' + str(self.value) + ']'

################################################################################

class TrappedError(Exception):
    pass


################################################################################
# Auxiliary Functions
################################################################################

# signed 64-bit arithmetic

min_int64 = -(1<<63)

max_int64 = (1<<63)-1

mask_64 = (1<<64)-1

offset_64 = 1<<63

def to_unsigned(x):
    return x & mask_64

def to_signed(x):
    return ((x + offset_64) & mask_64) - offset_64

def add64(x,y):
    return to_signed(x+y)

def sub64(x,y):
    return to_signed(x-y)

def mul64(x,y):
    return to_signed(x*y)

def neg64(x):
    return to_signed(-x)

def xor64(x,y):
    return to_signed(x^y)

def is_int64(x) -> bool:
    return isinstance(x,int) and (x >= min_int64 and x <= max_int64)

def input_int() -> int:
    # entering illegal characters may cause exception,
    # but we won't worry about that
    x = int(input())
    # clamp to 64 bit signed number, emulating behavior of C's scanf
    x = min(max_int64,max(min_int64,x))
    return x

def unzip(ls):
    xs, ys = [], []
    for (x, y) in ls:
        xs += [x]
        ys += [y]
    return (xs, ys)


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

emulate_x86 = False

def enable_tracing():
    global tracing
    tracing = True

def enable_emulation():
    global emulate_x86
    emulate_x86 = True


def trace(msg):
    if tracing:
        print(msg, file=sys.stderr)


def trace_ast_and_concrete(ast):
    trace("concrete syntax:")
    trace(ast)
    trace("")
    trace("AST:")
    trace(repr(ast))

def is_python_extension(filename):
    s = os.path.splitext(filename)
    if len(s) > 1:
        return s[1] == ".py"
    else:
        return False

class redirect_stdin(_RedirectStream):
    _stream = "stdin"

# Given the `ast` output of a pass and a test program (root) name,
# runs the interpreter on the program and compares the output to the
# expected "golden" output.
def test_pass(passname, interp_dict, program_root, ast,
              compiler_name):
    if passname in interp_dict.keys():
        input_file = program_root + '.in'
        if not os.path.isfile(input_file):
            input_file = "/dev/null"
        output_file = program_root + '.out'
        with open(input_file, 'r') as inf, open(output_file, 'w') as outf:
            with redirect_stdout(outf), redirect_stdin(inf):
                interp_dict[passname](ast)
        result = os.system('diff' + ' -b ' + output_file + ' ' + program_root + '.golden')
        if result == 0:
            trace('compiler ' + compiler_name + ' success on pass ' + passname \
                  + ' on test\n' + program_root + '\n')
            return 1
        else:
            print('compiler ' + compiler_name + ' failed pass ' + passname \
                  + ' on test\n' + program_root + '\n')
            return 0
    else:
        trace('compiler ' + compiler_name + ' skip test on pass ' + passname + ' on test\n' + program_root + '\n')
        return 0  # ??


def compile_and_test(compiler, program_filename):
    total_passes = 0
    successful_passes = 0
    from eval_x86 import interp_x86

    program_root = os.path.splitext(program_filename)[0]
    with open(program_filename) as source:
        program = parse(source.read())

    trace('\n# source program: ' + os.path.basename(program_root) + '\n')
    trace(program)
    trace('')

    if 'source' in compiler.type_check_dict.keys():
        trace('\n# type checking source program\n')
        compiler.type_check_dict['source'](program)

    passes = compiler.passes()
    for passname, passfn in passes:
        trace('\n# ' + passname + '\n')
        program = passfn(program)
        trace(program)
        trace('')
        if passname in compiler.typecheck_dict.keys():
            trace('compiler ' + compiler.compiler_name + ' type checking on pass ' + passname \
                  + ' on test ' + program_root + '\n')
            compiler.typecheck_dict[passname](program)
        total_passes += 1
        successful_passes += \
             test_pass(passname, compiler.interp_dict, program_root, program, compiler.compiler_name)

    x86_filename = program_root + ".s"
    with open(x86_filename, "w") as dest:
        dest.write(str(program))

    total_passes += 1

    # Run the final x86 program
    input_file = program_root + '.in'
    if not os.path.isfile(input_file):
        input_file = "/dev/null"
    output_file = program_root + '.out'
    if emulate_x86:
         trace('emulating x86')
         with open(input_file, 'r') as inf, open(output_file, 'w') as outf:
              with redirect_stdout(outf), redirect_stdin(inf):
                  interp_x86(program)
    else:
        trace('executing x86')
        arch = ' -arch x86_64' if platform == 'darwin' else ''
        x86_executable = program_root + '.exe'
        if os.path.isfile(x86_executable):
            os.remove(x86_executable)
        if os.path.isfile(output_file):
            os.remove(output_file)
        os.system('gcc' + arch + ' -o ' + x86_executable + ' runtime.o ' + x86_filename)
        os.system(x86_executable + ' < ' + input_file + ' > ' + output_file)

    result = os.system('diff' + ' -b ' + program_root + '.out ' \
                       + program_root + '.golden')
    if result == 0:
        successful_passes += 1
        return (successful_passes, total_passes, 1)
    else:
        print('compiler ' + compiler.compiler_name + ', executable failed' \
              + ' on test ' + program_root)
        return (successful_passes, total_passes, 0)


# This function compiles the program without any testing
def compile(compiler, program_filename):
    program_root = os.path.splitext(program_filename)[0]
    with open(program_filename) as source:
        program = parse(source.read())

    trace_ast_and_concrete(program)

    trace('\n# type check\n')
    compiler.typecheck_dict['source'](program)

    for passname, passfn in compiler.passes():
        trace('\n# ' + passname + '\n')
        perogram = passfn(program)
        trace_ast_and_concrete(program)

    # Output x86 program to the .s file
    x86_filename = program_root + ".s"
    with open(x86_filename, "w") as dest:
        dest.write(str(program))

# Given a test file name and a compiler, run all the passes in the compiler,
# checking that the resulting programs produce output that matches the
# golden file.
def run_one_test(test, compiler):
    try: 
        return compile_and_test(compiler, test)
    except Exception as exn:
        from traceback import print_exc
        print_exc(file=sys.stderr)
        return (0,0,0)

# Given the name <language> of a language and a compiler, 
# test the compiler on all the tests in ./tests/<language>
def run_tests(lang, compiler):
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
            run_one_test(test, compiler)
        successful_passes += succ_passes
        total_passes += tot_passes
        successful_tests += succ_test
        total_tests += 1

    # Report the pass/fails
    print('tests: ' + repr(successful_tests) + '/' + repr(total_tests) \
          + ' for compiler ' + compiler.compiler_name + ' on language ' + lang)
    print('passes: ' + repr(successful_passes) + '/' + repr(total_passes) \
          + ' for compiler ' + compiler.compiler_name + ' on language ' + lang)

# Given a list of file names and a compiler, 
# test the compiler on all the tests in the list.
def run_selected_tests(tests, compiler):
    # Compile and run each test program, comparing output to the golden file.
    successful_passes = 0
    total_passes = 0
    successful_tests = 0
    total_tests = 0
    for test in tests:
        print(test + ':', file=sys.stderr)
        (succ_passes, tot_passes, succ_test) = \
            run_one_test(test, compiler)
        successful_passes += succ_passes
        total_passes += tot_passes
        successful_tests += succ_test
        total_tests += 1

    # Report the pass/fails
    print('tests: ' + repr(successful_tests) + '/' + repr(total_tests) \
          + ' for compiler ' + compiler.compiler_name)
    print('passes: ' + repr(successful_passes) + '/' + repr(total_passes) \
          + ' for compiler ' + compiler.compiler_name)
    
