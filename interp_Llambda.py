from ast import *
from interp_Lfun import InterpLfun, Function
from utils import *

class InterpLlambda(InterpLfun):

  def interp_exp(self, e, env):
    match e:
      case FunRefArity(id, arity):
        return env[id]
      case Lambda(params, body):
        return Function('lambda', params, [Return(body)], env)
      case Closure(arity, args):
        return tuple([self.interp_exp(arg, env) for arg in args])
      case AllocateClosure(length, typ, arity):
        array = [None] * length
        return array
      case _:
        return super().interp_exp(e, env)
    
  def interp_stmts(self, ss, env):
    if len(ss) == 0:
      return
    match ss[0]:
      case AnnAssign(lhs, typ, value, simple):
        env[lhs.id] = self.interp_exp(value, env)
        return self.interp_stmts(ss[1:], env)
      case _:
        return super().interp_stmts(ss, env)
        
