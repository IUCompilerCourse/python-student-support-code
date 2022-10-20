from ast import *
from interp_Ltup import InterpLtup
from utils import *

class InterpLarray(InterpLtup):

  def interp_exp(self, e, env):
    match e:
      case ast.List(es, Load()):
        return [self.interp_exp(e, env) for e in es]
      case BinOp(left, Mult(), right):
          l = self.interp_exp(left, env); r = self.interp_exp(right, env)
          return mul64(l, r)
      case Subscript(tup, index, Load()):
        t = self.interp_exp(tup, env)
        n = self.interp_exp(index, env)
        if n < len(t):
          return t[n]
        else:
          raise TrappedError('array index out of bounds')
      case AllocateArray(length, typ):
        array = [None] * length
        return array
      case Call(Name('array_len'), [tup]):
        t = self.interp_exp(tup, env)
        return len(t)
      case Call(Name('array_load'), [tup, index]):
        t = self.interp_exp(tup, env)
        n = self.interp_exp(index, env)
        if n < len(t):
          return t[n]
        else:
          raise TrappedError('array index out of bounds')
      case Call(Name('array_store'), [tup, index, value]):
        t = self.interp_exp(tup, env)
        n = self.interp_exp(index, env)
        if n < len(t):
          t[n] = self.interp_exp(value, env)
        else:
          raise TrappedError('array index out of bounds')
        return None
      case _:
        return super().interp_exp(e, env)

  def interp_stmt(self, s, env, cont):
    match s:
      case Assign([Subscript(tup, index)], value):
        t = self.interp_exp(tup, env)
        n = self.interp_exp(index, env)
        if n < len(t):
          t[n] = self.interp_exp(value, env)
        else:
          raise TrappedError('array index out of bounds')
        return self.interp_stmts(cont, env)
      case _:
        return super().interp_stmt(s, env, cont)
