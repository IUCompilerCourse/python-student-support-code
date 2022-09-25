from ast import *
from interp_Lif import InterpLif
from utils import *

class InterpCif(InterpLif):

  def interp_stmt(self, s, env):
    match s:
      case Goto(label):
        self.interp_stmts(self.blocks[label], env)
      case Return(e): # return value doesn't really matter
        self.interp_exp(e,env)
      case _:
        super().interp_stmt(s, env)
    
  def interp(self, p):
    match p:
      case CProgram(blocks):
        env = {}
        self.blocks = blocks
        self.interp_stmts(blocks[label_name('start')], env)
    
