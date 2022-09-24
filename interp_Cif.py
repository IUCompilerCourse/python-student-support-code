from ast import *
from interp_Lif import InterpLif
from utils import *

class InterpCif(InterpLif):

  def interp_stmt(self, s, env, cont):
    match s:
      case Return(value):
        return self.interp_exp(value, env)
      case Goto(label):
        return self.interp_stmts(self.blocks[label], env)
      case _:
        return super().interp_stmt(s, env, cont)
    
  def interp(self, p):
    match p:
      case CProgram(blocks):
        env = {}
        self.blocks = blocks
        self.interp_stmts(blocks[label_name('start')], env)
    
