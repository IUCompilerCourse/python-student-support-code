from ast import *
from interp_Pif import InterpPif
from utils import *

class InterpCif(InterpPif):

  def interp_stmts(self, ss, env):
    if len(ss) == 0:
        return
    match ss[0]:
      case Return(value):
        return self.interp_exp(value, env)
      case Goto(label):
        return self.interp_stmts(self.CFG[label], env)
      case _:
        return super().interp_stmts(ss, env)
    
  def interp_C(self, p):
    match p:
      case CProgram(cfg):
        env = {}
        self.CFG = cfg
        self.interp_stmts(cfg[label_name('start')], env)
    
