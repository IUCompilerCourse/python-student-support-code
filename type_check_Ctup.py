from ast import *
from type_check_Cif import check_type_equal, Bottom
from type_check_Cwhile import TypeCheckCwhile
from utils import Allocate, Begin, GlobalValue, Collect, TupleType

class TypeCheckCtup(TypeCheckCwhile):
    
  def type_check_exp(self, e, env):
    match e:
        case Allocate(length, typ):
          return typ
        case Begin(ss, e):
          self.type_check_stmts(ss, env)
          return self.type_check_exp(e, env)
        case GlobalValue(name):
          return int
        case Subscript(tup, Constant(index), Load()):
          tup_t = self.type_check_atm(tup, env)
          match tup_t:
            case TupleType(ts):
              return ts[index]
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
      case Assign([Subscript(tup, Constant(index))], value):
        tup_t = self.type_check_atm(tup, env)
        value_t = self.type_check_atm(value, env)
        match tup_t:
          case TupleType(ts):
            check_type_equal(ts[index], value_t, s)
          case Bottom():
              pass
          case _:
            raise Exception('error, expected a tuple, not ' + repr(tup_t))
      case _:
        return super().type_check_stmt(s, env)
      
