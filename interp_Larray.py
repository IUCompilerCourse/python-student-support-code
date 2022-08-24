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
          return l * r
      case AllocateArray(length, typ):
        array = [None] * length
        return array
      case Call(Name('array_len'), [tup]):
        t = self.interp_exp(tup, env)
        return len(t)
      case Call(Name('array_load'), [tup, index]):
        t = self.interp_exp(tup, env)
        n = self.interp_exp(index, env)
        return t[n]
      case Call(Name('array_store'), [tup, index, value]):
        tup = self.interp_exp(tup, env)
        index = self.interp_exp(index, env)
        tup[index] = self.interp_exp(value, env)
        return None
      case _:
        return super().interp_exp(e, env)

  def interp_stmts(self, ss, env):
    if len(ss) == 0:
      return
    match ss[0]:
      case Assign([Subscript(tup, index)], value):
        tup = self.interp_exp(tup, env)
        index = self.interp_exp(index, env)
        tup[index] = self.interp_exp(value, env)
        return self.interp_stmts(ss[1:], env)
      case _:
        return super().interp_stmts(ss, env)
