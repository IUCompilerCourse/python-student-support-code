from ast import *
from type_check_Cwhile import TypeCheckCwhile
from utils import Allocate, Begin, GlobalValue, Collect, TupleType, Bottom, \
  IntType, BoolType

class TypeCheckCtup(TypeCheckCwhile):

  def check_type_equal(self, t1, t2, e):
    match t1:
      case TupleType(ts1):
        match t2:
          case TupleType(ts2):
            for (ty1, ty2) in zip(ts1,ts2):
              self.check_type_equal(ty1, ty2, e)
          case Bottom():
            pass
          case _:
            raise Exception('error: ' + repr(t1) + ' != ' + repr(t2) \
                      + ' in ' + repr(e))
      case _:
        super().check_type_equal(t1, t2, e)

  def type_check_atm(self, e, env):
    match e:
      case GlobalValue(name):
        return IntType()
      case _:
        return super().type_check_atm(e, env)
  
  def type_check_exp(self, e, env):
    match e:
        case Compare(left, [cmp], [right]) if isinstance(cmp, Is):
          l = self.type_check_exp(left, env)
          r = self.type_check_exp(right, env)
          self.check_type_equal(l, r, e)
          return BoolType()
        case Allocate(length, typ):
          return typ
        case Subscript(tup, Constant(index), Load()):
          tup_t = self.type_check_atm(tup, env)
          match tup_t:
            case TupleType(ts):
              return ts[index]
            case Bottom():
              return Bottom()
            case _:
              raise Exception('error, expected a tuple, not ' + repr(tup_t))
        case Call(Name('len'), [tup]):
          tup_t = self.type_check_atm(tup, env)
          match tup_t:
            case TupleType(ts):
              return IntType()
            case Bottom():
              return Bottom()
            case _:
              raise Exception('error, expected a tuple, not ' + repr(tup_t))
        case _:
          return super().type_check_exp(e, env)

  def type_check_stmt(self, s, env):
    match s:      
      case Collect(size):
        pass
      case Assign([Subscript(tup, Constant(index), Store())], value):
        tup_t = self.type_check_atm(tup, env)
        value_t = self.type_check_atm(value, env)
        match tup_t:
          case TupleType(ts):
            self.check_type_equal(ts[index], value_t, s)
          case Bottom():
              pass
          case _:
            raise Exception('type_check_stmt: expected a tuple, not ' \
                            + repr(tup_t))
      case _:
        return super().type_check_stmt(s, env)
      
