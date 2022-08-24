from ast import *
from interp_Llambda import InterpLlambda
from utils import *

class InterpLgeneric(InterpLlambda):

  def interp_exp(self, e, env):
    match e:
      case Inst(gen, type_args):
        return self.interp_exp(gen, env)
      case _:
        return super().interp_exp(e, env)

  def interp_stmts(self, ss, env):
    if len(ss) == 0:
      return
    match ss[0]:
      case ImportFrom():
        return self.interp_stmts(ss[1:], env)
      case Assign([Name(id)], Call(Name('TypeVar'), args)):
        return self.interp_stmts(ss[1:], env)
      case Pass():
        return self.interp_stmts(ss[1:], env)
      case _:
        return super().interp_stmts(ss, env)
        
    
