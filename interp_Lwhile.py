from ast import *
from interp_Lif import InterpLif
from utils import *

class InterpLwhile(InterpLif):

  def interp_stmt(self, s, env):
    match s:
      case While(test, body, []):
        while self.interp_exp(test, env):
            self.interp_stmts(body, env)
      case _:
        super().interp_stmt(s, env)
    
