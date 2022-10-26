from ast import *
from interp_Lif import InterpLif
from utils import *

class InterpCif(InterpLif):

  def interp(self, p):
    match p:
      case CProgram(blocks):
        env = {}
        self.blocks = blocks
        self.interp_stmts(blocks[label_name('start')], env)

  def interp_stmts(self, ss, env):
    match ss:
      case [t]:
        return self.interp_tail(t, env)
      case [s, *ss]:
        self.interp_stmt(s, env, [])
        return self.interp_stmts(ss, env)

  def interp_tail(self, s, env):
    match s:
      case Return(value):
        return self.interp_exp(value, env)
      case Goto(label):
        return self.interp_stmts(self.blocks[label], env)
      case If(test, [Goto(thn)], [Goto(els)]):
        match self.interp_exp(test, env):
          case True:
            return self.interp_stmts(self.blocks[thn], env)
          case False:
            return self.interp_stmts(self.blocks[els], env)
      case _:
        raise Exception('interp_tail: unexpected ' + repr(s))
