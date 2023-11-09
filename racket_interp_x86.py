#!/usr/bin/env python3

from x86_ast import *
from dataclasses import fields
import sys
import subprocess
import utils


def label_name_(n: str) -> str:
    if sys.platform == "darwin" and n.startswith("_"):
        return n[1:]
    else:
        return n


def convert_arg(arg):
    match arg:
        case Reg(id):
            return f"(Reg '{id})"
        case Variable(id):
            return f"(Var '{id})"
        case Immediate(value):
            return f"(Imm {value})"
        case Deref(reg, offset):
            return f"(Deref '{reg} {offset})"
        case ByteReg(id):
            return f"(ByteReg '{id})"
        case Global(id):
            return f"(Global '{label_name_(id)})"
        case _:
            raise Exception('convert_arg: unhandled ' + repr(arg))


def convert_instr(instr):
    match instr:
        case Instr(instr, [arg]) if instr.startswith('set'):
            cc = instr[3:]
            converted_arg = convert_arg(arg)
            return f"(Instr 'set (list '{cc} {converted_arg}))"
        case Instr(instr, args):
            converted_args = [convert_arg(arg) for arg in args]
            return f"(Instr '{instr} (list {' '.join(converted_args)}))"
        case Callq(func, args):
            return f"(Callq '{label_name_(func)} {args})"
        case IndirectCallq(arg, n):
            return f"(IndirectCallq {convert_arg(arg)} {n})"
        case Jump(label):
            return f"(Jmp '{label_name_(label)})"
        case TailJump(arg, n):
            return f"(TailJmp {convert_arg(arg)} {n})"
        case JumpIf(cc, label):
            return f"(JmpIf '{cc} '{label_name_(label)})"
        case _:
            raise Exception('convert_instr: unhandled ' + repr(instr))


def convert_body(body):
    if isinstance(body, list):
        main_instrs = [convert_instr(instr) for instr in body]
        return (f"`(({label_name_('main')} . "
                  f",(Block '() (list {' '.join(main_instrs)}))))")
    elif isinstance(body, dict):
        blocks = [(f"({label_name_(l)} . "
                    f",(Block '() (list "
                      f"{' '.join([convert_instr(instr) for instr in ss])})))")
                  for (l, ss) in body.items()]
        return f"`({' '.join(blocks)})"
    else:
        raise Exception('convert_body: unhandled ' + repr(body))


def convert_def(df):
    match df:
        case utils.FunctionDef(label, [], body, _, rtyp, _):
            info = convert_info(df)
            return (f"(Def '{label_name_(label)} '() '{convert_type(rtyp)}"
                    f" {info} {convert_body(body)})")
        case _:
            raise Exception('convert_def: unhandled ' + repr(df))


def convert_type(t):
    match t:
        case utils.IntType():
            return "Integer"
        case utils.BoolType():
            return "Boolean"
        case utils.VoidType():
            return "Void"
        case utils.Bottom():
            return "_"
        case utils.TupleType(types):
            return f"(Vector {' '.join([convert_type(typ) for typ in types])})"
        case utils.ListType(elt_type):
            return f"(Vectorof {elt_type})"
        case utils.FunctionType(param_types, ret_type):
            domains = ' '.join([convert_type(pt) for pt in param_types])
            return f"({domains} -> {convert_type(ret_type)})"
        case _:
            raise Exception('convert_type: unhandled ' + repr(t))


def convert_value(v):
    if isinstance(v, dict):
        pairs = [f"({convert_value(key)} . {convert_value(value)})"
                 for key, value in v.items()]
        return f"({' '.join(pairs)})"
    elif isinstance(v, list):
        return f"({' '.join([convert_value(mem) for mem in v])})"
    elif isinstance(v, utils.Type):
        return convert_type(v)
    elif isinstance(v, str):
        # strings in python will be treated as symbols in racket
        return f'{v}'
    elif isinstance(v, int):
        return f'{v}'
    else:
        raise Exception('convert_value: unhandled ' + repr(v))


def convert_info(node):
    all_fields = set(vars(node))
    # TODO: make sure "node" is a dataclass so that we don't have to hard code
    # c_fields
    c_fields = {'body', 'defs', 'name', 'args',
                'decorator_list', 'returns', 'type_comment',
                'type_params'} #set([f.name for f in fields(node)])
    info_fields = all_fields - c_fields
    pairs = [f"({info_field.replace('_', '-')} . "
               f"{convert_value(getattr(node, info_field))})"
             for info_field in info_fields]
    return f"'({' '.join(pairs)})"


def convert_ast(x86program):
    info = convert_info(x86program)
    match x86program:
        case X86ProgramDefs(defs):
            converted_defs = ' '.join([convert_def(df) for df in defs])
            return f"(X86ProgramDefs {info} (list {converted_defs}))"
        case X86Program(body):
            return f"(X86Program {info} {convert_body(body)})"
        case _:
            raise Exception('convert_ast: unhandled ' + repr(x86program))


def racket_interp_x86(program):
    _racket_interp_x86(program, False)


def racket_interp_pseudo_x86(program):
    _racket_interp_x86(program, True)


def _racket_interp_x86(program, is_pseudo):
    ast_str = convert_ast(program)
    interpreter = "interp-pseudo-x86-python" if is_pseudo else "interp-x86-python"
    racket_program = f"""
    (require "utilities.rkt")
    (require "interp.rkt")
    (define program {ast_str})
    (define result ({interpreter} program))
    (exit result)
    """
    result = subprocess.run(["racket", "-e", racket_program],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            stdin=sys.stdin,
                            cwd="../public-student-support-code",
                            text=True)
    print(result.stdout.rstrip(), end="")


if __name__ == "__main__":
    #TODO: interpet from file name provided as CLI argument
    #sys.stdin="42\n"
    racket_interp_x86(
        X86Program({'_block.6':
                    [Instr('negq', [Reg('rdi')]),
                     Callq('_print_int', 1),
                     Instr('movq', [Immediate(0), Reg('rax')]),
                     Jump('_conclusion')],
                    '_block.8': [Callq('_read_int', 0),
                                 Instr('movq', [Reg('rax'), Reg('rdi')]),
                                 Jump('_block.6')],
                    '_block.9': [Callq('_read_int', 0),
                                 Instr('movq', [Reg('rax'), Reg('rdi')]),
                                 Instr('negq', [Reg('rdi')]),
                                 Jump('_block.6')],
                    '_block.10':
                    [Instr('movq', [Global('_free_ptr'), Reg('r11')]),
                     Instr('addq', [Immediate(16), Global('_free_ptr')]),
                     Instr('movq', [Immediate(3), Deref('r11', 0)]),
                     Instr('movq', [Reg('r11'), Reg('rdi')]),
                     Instr('movq', [Reg('rdi'), Reg('r11')]),
                     Instr('movq', [Reg('rbx'), Deref('r11', 8)]),
                     Instr('movq', [Reg('rdi'), Reg('r11')]),
                     Instr('movq', [Deref('r11', 8), Reg('rdi')]),
                     Instr('cmpq', [Immediate(0), Reg('rdi')]),
                     JumpIf('e', '_block.8'),
                     Jump('_block.9')],
                    '_block.11':
                    [Instr('movq', [Reg('r15'), Reg('rdi')]),
                     Instr('movq', [Immediate(16), Reg('rsi')]),
                     Callq('_collect', 2),
                     Jump('_block.10')],
                    '_start':
                    [Instr('movq', [Immediate(1), Reg('rbx')]),
                     Instr('movq', [Global('_free_ptr'), Reg('rdi')]),
                     Instr('addq', [Immediate(16), Reg('rdi')]),
                     Instr('cmpq', [Global('_fromspace_end'), Reg('rdi')]),
                     JumpIf('l', '_block.10'),
                     Jump('_block.11')],
                    '_main':
                    [Instr('pushq', [Reg('rbp')]),
                     Instr('movq', [Reg('rsp'), Reg('rbp')]),
                     Instr('pushq', [Reg('rbx')]),
                     Instr('subq', [Immediate(8), Reg('rsp')]),
                     Instr('movq', [Immediate(65536), Reg('rdi')]),
                     Instr('movq', [Immediate(16), Reg('rsi')]),
                     Callq('_initialize', 2),
                     Instr('movq', [Global('_rootstack_begin'), Reg('r15')]),
                     Jump('_start')],
                    '_conclusion':
                    [Instr('subq', [Immediate(0), Reg('r15')]),
                     Instr('addq', [Immediate(8), Reg('rsp')]),
                     Instr('popq', [Reg('rbx')]),
                     Instr('popq', [Reg('rbp')]),
                     Instr('retq', [])]})
        )
