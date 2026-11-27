import ast
from ast import *
from type_check_Llambda import TypeCheckLlambda
from utils import *
import typing

class TypeCheckLany(TypeCheckLlambda):

  def parse_type_annot(self, annot):
      match annot:
        case Name('Any'):
          return AnyType()
        case AnyType():
          return AnyType()
        case _:
          return super().parse_type_annot(annot)
        
  def type_check_exp(self, e, env):
    match e:
      case Inject(value, typ):
        self.check_exp(value, typ, env)
        return AnyType()
      case Project(value, typ):
        self.check_exp(value, AnyType(), env)
        return typ
      case Call(Name(atl), [tup, index]) \
          if atl == 'any_load' or atl == 'any_load_unsafe':
        self.check_exp(tup, AnyType(), env)
        self.check_exp(index, IntType(), env)
        return AnyType()
      case Call(Name(atl), [tup, index, value]) \
          if atl == 'any_store' or atl == 'any_store_unsafe':
        self.check_exp(tup, AnyType(), env)
        self.type_check_exp(value, env)
        self.check_exp(index, IntType(), env)
        return VoidType()
      case Call(Name('any_len'), [tup]):
        self.check_exp(tup, AnyType(), env)
        return IntType()
      case Call(Name('arity'), [fun]):
        ty = self.type_check_exp(fun, env)
        match ty:
          case FunctionType(ps, rt):
            return IntType()
          case TupleType([FunctionType(ps,rs)]):
            return IntType()
          case _:
            raise Exception('type_check_exp arity unexpected ' + repr(ty))
      case Call(Name('make_any'), [value, tag]):
        self.type_check_exp(value, env)
        self.check_exp(tag, IntType(), env)
        return AnyType()
      case ValueOf(value, typ):
        self.check_exp(value, AnyType(), env)
        return typ
      case TagOf(value):
        self.check_exp(value, AnyType(), env)
        return IntType()
      case AnnLambda(params, returns, body):
        new_env = {x:t for (x,t) in env.items()}
        for (x,t) in params:
            new_env[x] = t
        return_t = self.type_check_exp(body, new_env)
        self.check_type_equal(returns, return_t, e)
        return FunctionType([t for (x,t) in params], return_t)
      case _:
        return super().type_check_exp(e, env)
