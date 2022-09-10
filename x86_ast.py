from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import List

from utils import dedent, indent, indent_stmt, label_name


@dataclass(frozen=True)
class X86Program:
    body: dict[str, list[instr]] | list[instr]

    def __str__(self):
        result = ''
        if isinstance(self.body, dict):
            for (l,ss) in self.body.items():
                if l == label_name('main'):
                    result += '\t.globl ' + label_name('main') + '\n'
                result += '\t.align 16\n'
                result += l + ':\n'
                indent()
                result += ''.join([str(s) for s in ss]) + '\n'
                dedent()
        else:
            result += '\t.globl ' + label_name('main') + '\n' + \
                      label_name('main') + ':\n'
            indent()
            result += ''.join([str(s) for s in self.body])
            dedent()
        result += '\n'
        return result

@dataclass(frozen=True)
class X86ProgramDefs:
    defs: list[ast.FunctionDef]

    def __str__(self):
        return "\n".join([str(d) for d in self.defs])

class instr: ...
class arg: ...
class location(arg): ...

@dataclass(frozen=True)
class Instr(instr):
    instr: str
    args: List[arg]

    def source(self):
        return self.args[0]
    def target(self):
        return self.args[-1]
    def __str__(self):
        return indent_stmt() + self.instr + ' ' + ', '.join(str(a) for a in self.args) + '\n'

@dataclass(frozen=True)
class Callq(instr):
    func: str
    num_args: int

    def __str__(self):
        return indent_stmt() + 'callq' + ' ' + self.func + '\n'

@dataclass(frozen=True)
class IndirectCallq(instr):
    func: arg
    num_args: int

    def __str__(self):
        return indent_stmt() + 'callq' + ' *' + str(self.func) + '\n'

@dataclass(frozen=True)
class JumpIf(instr):
    cc: str
    label: str

    def __str__(self):
        return indent_stmt() + 'j' + self.cc + ' ' + self.label + '\n'

@dataclass(frozen=True)
class Jump(instr):
    label: str

    def __str__(self):
        return indent_stmt() + 'jmp ' + self.label + '\n'

@dataclass(frozen=True)
class IndirectJump(instr):
    target: location

    def __str__(self):
        return indent_stmt() + 'jmp *' + str(self.target) + '\n'

@dataclass(frozen=True)
class TailJump(instr):
    func: arg
    arity: int

    def __str__(self):
        return indent_stmt() + 'tailjmp ' + str(self.func) + '\n'

@dataclass(frozen=True)
class Variable(location):
    id: str

    def __str__(self):
        return self.id

@dataclass(frozen=True)
class Immediate(arg):
    value: int

    def __str__(self):
        return '$' +  str(self.value)

@dataclass(frozen=True)
class Reg(location):
    id: str

    def __str__(self):
        return '%' + self.id

@dataclass(frozen=True)
class ByteReg(Reg):
    pass

@dataclass(frozen=True)
class Deref(arg):
    reg: str
    offset: int

    def __str__(self):
        return str(self.offset) + '(%' + self.reg + ')'

@dataclass(frozen=True)
class Global(arg):
    name: str

    def __str__(self):
        return self.name + "(%rip)"
