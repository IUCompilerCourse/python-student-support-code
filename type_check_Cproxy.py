from type_check_Cany import TypeCheckCany
from utils import *

class TypeCheckCproxy(TypeCheckCany):

  def check_type_equal(self, t1, t2, e):
    if t1 == Bottom() or t2 == Bottom():
      return
    match t1:
      case ProxyOrListType(elt1):
        match t2:
          case ProxyOrListType(elt2):
              self.check_type_equal(elt1, elt2, e)
          case _:
            raise Exception('error: ' + repr(t1) + ' != ' + repr(t2) \
                            + ' in ' + repr(e))
      case ProxyOrTupleType(ps1):
        match t2:
          case ProxyOrTupleType(ps2):
            for (p1,p2) in zip(ps1, ps2):
              self.check_type_equal(p1, p2, e)
          case _:
            raise Exception('error: ' + repr(t1) + ' != ' + repr(t2) \
                            + ' in ' + repr(e))
      case _:
        super().check_type_equal(t1, t2, e)
    
  def type_check_exp(self, e, env):
    match e:
      case InjectTupleProxy(value, tup_typ):
        self.type_check_exp(value, env)
        # TODO: check the type of the value
        match tup_typ:
          case TupleType(ts):
            return ProxyOrTupleType(ts)
          case _:
            raise Exception('type_check error ' + repr(e))
      case InjectTuple(value):
        tup_ty = self.type_check_exp(value, env)
        match tup_ty:
          case TupleType(ts):
            return ProxyOrTupleType(ts)
          case _:
            raise Exception('type_check error ' + repr(e))
      case InjectListProxy(value, tup_typ):
        self.type_check_exp(value, env)
        # TODO: check the type of the value
        match tup_typ:
          case ListType(ty):
            return ProxyOrListType(ty)
          case _:
            raise Exception('type_check error ' + repr(e))
      case InjectList(value):
        tup_ty = self.type_check_exp(value, env)
        match tup_ty:
          case ListType(elt_ty):
            return ProxyOrListType(elt_ty)
          case _:
            raise Exception('type_check error ' + repr(e))
      case _:
        return super().type_check_exp(e, env)

  def type_check_stmt(self, s, env):
    match s:      
      case Assign([Call(Name('proxy_array_load'), [tup, index])], value):
        tup_t = self.type_check_exp(tup, env)
        value_t = self.type_check_exp(value, env)
        index_ty = self.type_check_exp(index, env)
        self.check_type_equal(index_ty, IntType(), index)
        match tup_t:
          case ProxyOrListType(ty):
            self.check_type_equal(ty, value_t, s)
          case Bottom():
            pass
          case _:
            raise Exception('type_check_stmts: expected a proxy-or-list, not ' \
                            + repr(tup_t))
      case _:
        super().type_check_stmt(s, env)
      
    
