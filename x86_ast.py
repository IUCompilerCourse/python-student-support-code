from typing import List

class X86Program:
    __match_args__ = ("body",)
    def __init__(self, body):
        self.body = body
    def __repr__(self):
        result = ''
        if type(self.body) == dict:
            for (l,ss) in self.body.items():
                result += l + ':\n'
                result += '\n'.join([repr(s) for s in ss]) + '\n\n'
        else:
            result = '\n'.join([repr(s) for s in self.body])
        return result
                
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
    def __repr__(self):
        return self.instr + ' ' + ', '.join(repr(a) for a in self.args)
    
class Callq(instr):
    __match_args__ = ("func", "num_args")
    def __init__(self, func, num_args):
        self.func = func
        self.num_args = num_args
    def __repr__(self):
        return 'callq' + ' ' + self.func
    
class Variable(location):
    __match_args__ = ("id",)
    def __init__(self, id):
        self.id = id
    def __repr__(self):
        return self.id
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
    def __repr__(self):
        return repr(self.value)
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
    def __repr__(self):
        return '%' + self.id
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
    def __repr__(self):
        return '%' + self.id
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
    def __repr__(self):
        return repr(self.offset) + '(%' + self.reg + ')'
    def __eq__(self, other):
        if isinstance(other, Deref):
            return self.reg == other.reg and self.offset == other.offset
        else:
            return False
    def __hash__(self):
        return hash((self.reg, self.offset))

class JumpIf(instr):
    cc: str
    label: str
    
    __match_args__ = ("cc", "label")
    def __init__(self, cc, label):
        self.cc = cc
        self.label = label
    def __repr__(self):
        return 'j' + self.cc + ' ' + self.label

class Jump(instr):
    label: str
    
    __match_args__ = ("label",)
    def __init__(self, label):
        self.label = label
    def __repr__(self):
        return 'jmp ' + self.label
