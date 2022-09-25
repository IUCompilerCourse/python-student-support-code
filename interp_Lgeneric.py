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

  def interp_stmt(self, s, env):
    match s:
      case ImportFrom():
        pass 
      case Assign([Name(id)], Call(Name('TypeVar'), args)):
        pass
      case Pass():
        pass 
      case _:
        return super().interp_stmts(ss, env)
        
    
