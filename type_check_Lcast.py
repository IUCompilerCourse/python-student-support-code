import ast
from ast import *
from type_check_Llambda import TypeCheckLlambda
from type_check_Lgrad import TypeCheckLgrad
from utils import *
import typing

class TypeCheckLcast(TypeCheckLlambda):

  def parse_type_annot(self, annot):
      match annot:
        case AnyType():
          return AnyType()
        case _:
          return super().parse_type_annot(annot)
      
  def type_check_exp(self, e, env):
    #trace('*** type_check_exp: ' + str(e) + '\nenv: ' + str(env))
    match e:
      case Cast(value, source, target):
        self.check_exp(value, source, env)
        TypeCheckLgrad().check_consistent(source, target, e)
        return target
      case AnnLambda(params, returns, body):
        new_env = {x:t for (x,t) in env.items()}
        for (x,t) in params:
            new_env[x] = t
        return_t = self.type_check_exp(body, new_env)
        self.check_type_equal(returns, return_t, e)
        return FunctionType([t for (x,t) in params], return_t)
      case Call(Name('any_load'), [tup, index]):
        self.check_exp(tup, AnyType(), env)
        self.check_exp(index, IntType(), env)
        return AnyType()
      case Call(Name('any_store'), [tup, index, value]):
        self.check_exp(tup, AnyType(), env)
        self.type_check_exp(value, env)
        self.check_exp(index, IntType(), env)
        return VoidType()
      case Call(Name('any_len'), [tup]):
        self.check_exp(tup, AnyType(), env)
        return IntType()
      case _:
        return super().type_check_exp(e, env)
