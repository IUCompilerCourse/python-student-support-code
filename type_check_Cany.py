from type_check_Clambda import TypeCheckClambda
from utils import *

class TypeCheckCany(TypeCheckClambda):
    
  def type_check_exp(self, e, env):
    match e:
      case ValueOf(value, typ):
        self.type_check_exp(value, env)
        return typ
      case TagOf(value):
        t = self.type_check_exp(value, env)
        self.check_type_equal(t, AnyType(), e)
        return IntType()
      case Call(Name('any_tuple_load'), [tup, index]):
        t = self.type_check_exp(tup, env)
        self.check_type_equal(t, AnyType(), e)
        return AnyType()
      case Call(Name('any_tuple_store'), [tup, index, value]):
        t = self.type_check_exp(tup, env)
        self.check_type_equal(t, AnyType(), e)
        v = self.type_check_exp(value, env)
        self.check_type_equal(v, AnyType(), e)
        return type(None) # ??
      case Call(Name('any_len'), [tup]):
        t = self.type_check_exp(tup, env)
        self.check_type_equal(t, AnyType(), e)
        return IntType()
      case Call(Name('make_any'), [value, tag]):
        v = self.type_check_exp(value, env)
        t = self.type_check_exp(tag, env)
        self.check_type_equal(t, IntType(), e)
        return AnyType()
      case Call(Name('exit'), []):
        return Bottom()
      case Call(Name('arity'), [fun]):
        ty = self.type_check_exp(fun, env)
        match ty:
          case FunctionType(ps, rt):
            return IntType()
          case TupleType([FunctionType(ps,rs)]):  # after closure conversion
            return IntType()
          case _:
            raise Exception('type_check_exp arity unexpected ' + repr(ty))
      case _:
        return super().type_check_exp(e, env)
   
