from ast import *
from type_check_Lif import TypeCheckLif
from utils import *

class TypeCheckLwhile(TypeCheckLif):

  def type_check_stmts(self, ss, env):
    if len(ss) == 0:
      return
    match ss[0]:
      case While(test, body, []):
        test_t = self.type_check_exp(test, env)
        self.check_type_equal(BoolType(), test_t, test)
        body_t = self.type_check_stmts(body, env)
        return self.type_check_stmts(ss[1:], env)
      case _:
        return super().type_check_stmts(ss, env)
    
