from ast import *
from type_check_Lvar import check_type_equal
from type_check_Lwhile import TypeCheckLwhile
from utils import *
import typing

class TypeCheckLtup(TypeCheckLwhile):

  def type_check_exp(self, e, env):
    match e:
      case Compare(left, [cmp], [right]) if isinstance(cmp, Is):
        l = self.type_check_exp(left, env)
        r = self.type_check_exp(right, env)
        check_type_equal(l, r, e)
        return bool
      case Tuple(es, Load()):
        ts = [self.type_check_exp(e, env) for e in es]
        e.has_type = TupleType(ts)
        return e.has_type
      case Subscript(tup, Constant(index), Load()):
        tup_ty = self.type_check_exp(tup, env)
        index_ty = self.type_check_exp(Constant(index), env)
        check_type_equal(index_ty, int, index)
        match tup_ty:
          case TupleType(ts):
            return ts[index]
          case _:
            raise Exception('error: expected a tuple, not ' + repr(tup_ty))
      case _:
        return super().type_check_exp(e, env)

if __name__ == "__main__":
  t1 = Tuple([Constant(1), Constant(2)], Load())
  t1_at_0 = Subscript(t1, Constant(0), Load())
  pr = Expr(Call(Name('print'), [t1_at_0]))
  p = Module([pr])
  TypeCheckLtup().type_check(p)
    
    
