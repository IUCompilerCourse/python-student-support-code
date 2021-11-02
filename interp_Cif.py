from ast import *
from interp_Lif import InterpLif
from utils import *

class InterpCif(InterpLif):

  def interp_stmts(self, ss, env):
    if len(ss) == 0:
        return
    match ss[0]:
      case Return(value):
        return self.interp_exp(value, env)
      case Goto(label):
        return self.interp_stmts(self.blocks[label], env)
      case _:
        return super().interp_stmts(ss, env)
    
  def interp_C(self, p):
    match p:
      case CProgram(blocks):
        env = {}
        self.blocks = blocks
        self.interp_stmts(cfg[label_name('start')], env)
    
