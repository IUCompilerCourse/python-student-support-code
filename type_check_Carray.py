from ast import *
from type_check_Ctup import TypeCheckCtup
from utils import Allocate, Begin, GlobalValue, Collect, TupleType, Bottom, \
  IntType, BoolType, ListType, AllocateArray, VoidType

class TypeCheckCarray(TypeCheckCtup):

  def check_type_equal(self, t1, t2, e):
    match t1:
      case ListType(ty1):
        match t2:
          case ListType(ty2):
              self.check_type_equal(ty1, ty2, e)
          case Bottom():
            pass
          case _:
            raise Exception('error: ' + repr(t1) + ' != ' + repr(t2) \
                      + ' in ' + repr(e))
      case _:
        super().check_type_equal(t1, t2, e)
  
  def type_check_exp(self, e, env):
    match e:
        case Subscript(tup, index, Load()):
          tup_ty = self.type_check_exp(tup, env)
          index_ty = self.type_check_exp(index, env)
          self.check_type_equal(index_ty, IntType(), index)
          match tup_ty:
            case TupleType(ts):
              match index:
                case Constant(i):
                  return ts[i]
                case _:
                  raise Exception('subscript required constant integer index')
            case ListType(ty):
              return ty
            case Bottom():
              return Bottom()
            case _:
              raise Exception('subscript expected a tuple, not ' + repr(tup_ty))
        case Call(Name('array_load'), [lst, index]):
          lst_ty = self.type_check_exp(lst, env)
          index_ty = self.type_check_exp(index, env)
          self.check_type_equal(index_ty, IntType(), index)
          match lst_ty:
            case ListType(ty):
              return ty
            case Bottom():
              return Bottom() 
            case _:
              raise Exception('array_load: unexpected ' + repr(lst_ty))
        case Call(Name('array_store'), [tup, index, value]):
          tup_t = self.type_check_exp(tup, env)
          value_t = self.type_check_exp(value, env)
          index_ty = self.type_check_exp(index, env)
          self.check_type_equal(index_ty, IntType(), index)
          match tup_t:
            case ListType(ty):
              self.check_type_equal(ty, value_t, e)
              return VoidType()
            case Bottom():
              return VoidType()
            case _:
              raise Exception('type_check_exp: expected a list, not ' \
                              + repr(tup_t))
        case AllocateArray(length, typ):
          return typ
        case Call(Name('len'), [tup]):
          tup_t = self.type_check_atm(tup, env)
          match tup_t:
            case TupleType(ts):
              return IntType()
            case Bottom():
              return Bottom()
            case _:
              raise Exception('error, expected a tuple, not ' + repr(tup_t))
        case Call(Name('array_len'), [tup]):
          tup_t = self.type_check_atm(tup, env)
          match tup_t:
            case ListType(ty):
              return IntType()
            case Bottom():
              return Bottom()
            case _:
              raise Exception('error, expected a list, not ' + repr(tup_t))
        case BinOp(left, Mult(), right):
          l = self.type_check_exp(left, env)
          self.check_type_equal(l, IntType(), left)
          r = self.type_check_exp(right, env)
          self.check_type_equal(r, IntType(), right)
          return IntType()
        case _:
          return super().type_check_exp(e, env)

  def type_check_stmt(self, s, env):
    match s:      
      case Assign([Subscript(tup, index, Store())], value):
        tup_t = self.type_check_atm(tup, env)
        value_t = self.type_check_atm(value, env)
        index_ty = self.type_check_exp(index, env)
        self.check_type_equal(index_ty, IntType(), index)
        match tup_t:
          case TupleType(ts):
            match index:
              case Constant(i):
                self.check_type_equal(ts[i], value_t, s)
              case _:
                raise Exception('subscript required constant integer index')
          case ListType(ty):
            self.check_type_equal(ty, value_t, s)
          case Bottom():
              pass
          case _:
            raise Exception('type_check_stmt: expected a tuple, not ' \
                            + repr(tup_t))
      case _:
        super().type_check_stmt(s, env)
      
