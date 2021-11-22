from ast import *
from interp_Cfun import InterpCfun
from utils import *

class InterpClambda(InterpCfun):

  def interp_exp(self, e, env):
    match e:
      case AllocateClosure(length, typ, arity):
        array = [None] * length
        return array
      case _:
        return super().interp_exp(e, env)
