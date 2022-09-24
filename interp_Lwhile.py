from ast import *
from interp_Lif import InterpLif
from utils import *

class InterpLwhile(InterpLif):

  def interp_stmt(self, s, env, cont):
    match s:
      case While(test, body, []):
        if self.interp_exp(test, env):
            self.interp_stmts(body + [s] + cont, env)
        else:
          return self.interp_stmts(cont, env)
      case _:
        return super().interp_stmt(s, env, cont)
    
