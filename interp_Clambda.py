from ast import *
from interp_Cfun import InterpCfun
from interp_Llambda import ClosureTuple
from utils import *
from interp_Lfun import Function

class InterpClambda(InterpCfun):

  def arity(self, v):
    match v:
      case Function(name, params, body, env):
        return len(params)
      case ClosureTuple(args, arity):
        return arity
      case _:
        raise Exception('Cany arity unexpected ' + repr(v))
    
  def interp_exp(self, e, env):
    match e:
      case Call(Name('arity'), [fun]):
        f = self.interp_exp(fun, env)
        return self.arity(f)
      case Uninitialized(ty):
        return None
      case AllocateClosure(length, typ, arity):
        array = [None] * length
        return ClosureTuple(array, arity)
      case _:
        return super().interp_exp(e, env)
