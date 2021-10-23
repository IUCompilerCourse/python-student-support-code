from typing import List
from utils import label_name, indent, dedent, indent_stmt

class X86Program:
    __match_args__ = ("body",)
    def __init__(self, body):
        self.body = body
    def __str__(self):
        result = ''
        if type(self.body) == dict:
            for (l,ss) in self.body.items():
                if l == label_name('main'):
                    result += '\t.globl ' + label_name('main') + '\n'
                result += l + ':\n'
                indent()
                result += '\n'.join([str(s) for s in ss]) + '\n\n'
                dedent()
        else:
            result += '\t.globl ' + label_name('main') + '\n' + \
                      label_name('main') + ':\n'
            indent()
            result += '\n'.join([str(s) for s in self.body])
            dedent()
        result += '\n'
        return result
    def __repr__(self):
        return 'X86Program(' + repr(self.body) + ')'
                
class instr: ...
class arg: ...
class location(arg): ...
    
class Instr(instr):
    instr: str
    args: List[arg]
    
    __match_args__ = ("instr", "args")
    def __init__(self, instr, args):
        self.instr = instr
        self.args = args
    def source(self):
        return self.args[0]
    def target(self):
        return self.args[-1]
    def __str__(self):
        return indent_stmt() + self.instr + ' ' + ', '.join(str(a) for a in self.args)
    def __repr__(self):
        return 'Instr(' + repr(self.instr) + ', ' + repr(self.args) + ')'
    
class Callq(instr):
    __match_args__ = ("func", "num_args")
    def __init__(self, func, num_args):
        self.func = func
        self.num_args = num_args
    def __str__(self):
        return indent_stmt() + 'callq' + ' ' + self.func
    def __repr__(self):
        return 'Callq(' + repr(self.func) + ', ' + repr(self.num_args) + ')'
    
class JumpIf(instr):
    cc: str
    label: str
    
    __match_args__ = ("cc", "label")
    def __init__(self, cc, label):
        self.cc = cc
        self.label = label
    def __str__(self):
        return indent_stmt() + 'j' + self.cc + ' ' + self.label
    def __repr__(self):
        return 'JumpIf(' + repr(self.cc) + ', ' + repr(self.label) + ')'

class Jump(instr):
    label: str
    
    __match_args__ = ("label",)
    def __init__(self, label):
        self.label = label
    def __str__(self):
        return indent_stmt() + 'jmp ' + self.label
    def __repr__(self):
        return 'Jump(' + repr(self.label) + ')'

class Variable(location):
    __match_args__ = ("id",)
    def __init__(self, id):
        self.id = id
    def __str__(self):
        return self.id
    def __repr__(self):
        return 'Variable(' + repr(self.id) + ')'
    def __eq__(self, other):
        if isinstance(other, Variable):
            return self.id == other.id
        else:
            return False
    def __hash__(self):
        return hash(self.id)

class Immediate(arg):
    __match_args__ = ("value",)
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return '$' +  str(self.value)
    def __repr__(self):
        return 'Immediate(' +  repr(self.value) + ')'
    def __eq__(self, other):
        if isinstance(other, Immediate):
            return self.value == other.value
        else:
            return False
    def __hash__(self):
        return hash(self.value)
    
class Reg(location):
    __match_args__ = ("id",)
    def __init__(self, id):
        self.id = id
    def __str__(self):
        return '%' + self.id
    def __repr__(self):
        return 'Reg(' + repr(self.id) + ')'
    def __eq__(self, other):
        if isinstance(other, Reg):
            return self.id == other.id
        else:
            return False
    def __hash__(self):
        return hash(self.id)
        
class ByteReg(arg):
    __match_args__ = ("id",)
    def __init__(self, id):
        self.id = id
    def __str__(self):
        return '%' + self.id
    def __repr__(self):
        return 'ByteReg(' + repr(self.id) + ')'
    def __eq__(self, other):
        if isinstance(other, ByteReg):
            return self.id == other.id
        else:
            return False
    def __hash__(self):
        return hash(self.id)
        
class Deref(arg):
    __match_args__ = ("reg", "offset")
    def __init__(self, reg, offset):
        self.reg = reg
        self.offset = offset
    def __str__(self):
        return str(self.offset) + '(%' + self.reg + ')'
    def __repr__(self):
        return 'Deref(' + repr(self.reg) + ', ' + repr(self.offset) + ')'
    def __eq__(self, other):
        if isinstance(other, Deref):
            return self.reg == other.reg and self.offset == other.offset
        else:
            return False
    def __hash__(self):
        return hash((self.reg, self.offset))

class Global(arg):
    __match_args__ = ("name",)
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return str(self.name) + "(%rip)"
    def __repr__(self):
        return 'GlobaleValue(' + repr(self.name) + ')'
    
