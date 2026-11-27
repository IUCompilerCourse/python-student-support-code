from utils import AllocateClosure, Uninitialized, UncheckedCast
from type_check_Cfun import TypeCheckCfun

class TypeCheckClambda(TypeCheckCfun):
    
  def type_check_exp(self, e, env):
    match e:
      case Uninitialized(ty):
        return ty
      case AllocateClosure(length, typ, arity):
        return typ
      case UncheckedCast(exp, ty):
        self.type_check_exp(exp, env)
        return ty
      case _:
        return super().type_check_exp(e, env)
   
