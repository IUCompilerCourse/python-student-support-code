from ast import *
from interp_Lwhile import InterpLwhile
from utils import *

class InterpLtup(InterpLwhile):

  def interp_cmp(self, cmp):
    match cmp:
      case Is():
        return lambda x, y: x is y
      case _:
        return super().interp_cmp(cmp)      
    
  def interp_exp(self, e, env):
    match e:
      case Tuple(es, Load()):
        # use a list for mutability
        return [self.interp_exp(e, env) for e in es]
      case Subscript(tup, index, Load()):
        t = self.interp_exp(tup, env)
        n = self.interp_exp(index, env)
        return t[n]
      case Call(Name('len'), [tup]):
        t = self.interp_exp(tup, env)
        return len(t)
      case Allocate(length, typ):
        array = [None] * length
        return array
      case GlobalValue(name):
        return 0 # ???
      case _:
        return super().interp_exp(e, env)

  def interp_stmt(self, s, env, cont):
    match s:
      case Collect(size):
        return self.interp_stmts(cont, env)
      case Assign([Subscript(tup, index)], value):
        tup = self.interp_exp(tup, env)
        index = self.interp_exp(index, env)
        tup[index] = self.interp_exp(value, env)
        return self.interp_stmts(cont, env)
      case _:
        return super().interp_stmt(s, env, cont)
    
if __name__ == "__main__":
  t1 = Tuple([Constant(1), Constant(2)], Load())
  t1_at_0 = Subscript(t1, Constant(0), Load())
  pr = Expr(Call(Name('print'), [t1_at_0]))
  p = Module([pr])
  InterpLtup().interp(p)
    
