import ast
from ast import *
from type_check_Lany import TypeCheckLany
from utils import *
import typing

class TypeCheckLproxy(TypeCheckLany):

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
    
  def parse_type_annot(self, annot):
      match annot:
        case ProxyOrTupleType(elt_types):
          return ProxyOrTupleType([self.parse_type_annot(t) for t in elt_types])
        case ProxyOrListType(elt_type):
          return ProxyOrListType(self.parse_type_annot(elt_type))
        case _:
          return super().parse_type_annot(annot)
      
  def type_check_exp(self, e, env):
    match e:
      # raw_tuple is just like Tuple
      case RawTuple(es):
        ts = [self.type_check_exp(e, env) for e in es]
        e.has_type = TupleType(ts)
        return e.has_type
      case TupleProxy(tup, reads, source, target):
        self.check_exp(tup, source, env)
        self.type_check_exp(reads, env)
        # TODO: check the types of reads and writes
        return target
      case ListProxy(lst, read, write, source, target):
        self.check_exp(lst, source, env)
        self.type_check_exp(read, env)
        self.type_check_exp(write, env)
        # TODO: check the types of read and write
        return target
      case InjectTuple(value):
        tup_ty = self.type_check_exp(value, env)
        match tup_ty:
          case TupleType(ts):
            return ProxyOrTupleType(ts)
          case _:
            raise Exception('type_check error ' + repr(e))
      case InjectTupleProxy(value, tup_ty):
        self.type_check_exp(value, env)
        # TODO: check the type of the value
        match tup_ty:
          case TupleType(ts):
            return ProxyOrTupleType(ts)
          case _:
            raise Exception('type_check error ' + repr(e))
      case InjectList(value):
        list_ty = self.type_check_exp(value, env)
        match list_ty:
          case ListType(elt_ty):
            return ProxyOrListType(elt_ty)
          case _:
            raise Exception('type_check error ' + repr(e))
      case InjectListProxy(value, list_ty):
        self.type_check_exp(value, env)
        # TODO: check the type of the value
        match list_ty:
          case ListType(elt_ty):
            return ProxyOrListType(elt_ty)
          case _:
            raise Exception('type_check error ' + repr(e))
      case Call(Name('is_tuple_proxy'), [arg]):
        arg_ty = self.type_check_exp(arg, env)
        match arg_ty:
          case ProxyOrTupleType(ts):
            return BoolType()
          case _:
            raise Exception('type_check error: expected ProxyOrTupleType, not ' + repr(arg_ty)
                            + ' in ' + repr(e))
      case Call(Name('is_array_proxy'), [arg]):
        arg_ty = self.type_check_exp(arg, env)
        match arg_ty:
          case ProxyOrListType(ts):
            return BoolType()
          case _:
            raise Exception('type_check error: expected ProxyOrListType, not ' + repr(arg_ty))
      case Call(Name('proxy_tuple_load'), [tup, Constant(index)]):
        tup_ty = self.type_check_exp(tup, env)
        match tup_ty:
          case ProxyOrTupleType(ts):
            return ts[index]
          case _:
            raise Exception('type_check error: expected ProxyOrTupleType, not ' + repr(tup_ty))
      case Call(Name('project_tuple'), [arg]):
        arg_ty = self.type_check_exp(arg, env)
        match arg_ty:
          case ProxyOrTupleType(ts):
            return TupleType(ts)
          case _:
            raise Exception('type_check error: expected ProxyOrTupleType, not ' + repr(arg_ty))
      case Call(Name('proxy_tuple_len'), [tup]):
        tup_ty = self.type_check_exp(tup, env)
        match tup_ty:
          case ProxyOrTupleType(ts):
            return IntType()
          case _:
            raise Exception('type_check error: expected ProxyOrListType, not ' + repr(tup_ty))
      case Call(Name('project_array'), [arg]):
        arg_ty = self.type_check_exp(arg, env)
        match arg_ty:
          case ProxyOrListType(elt_ty):
            return ListType(elt_ty)
          case _:
            raise Exception('type_check error: expected ProxyOrListType, not ' + repr(arg_ty))
      case Call(Name('proxy_array_len'), [tup]):
        tup_ty = self.type_check_exp(tup, env)
        match tup_ty:
          case ProxyOrListType(ts):
            return IntType()
          case _:
            raise Exception('type_check error: expected ProxyOrListType, not ' + repr(tup_ty))
      case Call(Name('proxy_array_load'), [lst, index]):
        lst_ty = self.type_check_exp(lst, env)
        index_ty = self.type_check_exp(index, env)
        self.check_type_equal(index_ty, IntType(), index)
        match lst_ty:
          case ProxyOrListType(ty):
            return ty
          case _:
            raise Exception('proxy_array_load expected a proxy-or-list, not ' + repr(lst_ty))
      case Call(Name('proxy_array_store'), [tup, index, value]):
        tup_t = self.type_check_exp(tup, env)
        value_t = self.type_check_exp(value, env)
        index_ty = self.type_check_exp(index, env)
        self.check_type_equal(index_ty, IntType(), index)
        match tup_t:
          case ProxyOrListType(ty):
            self.check_type_equal(ty, value_t, e)
            return VoidType()
          case Bottom():
            return VoidType()
          case _:
            raise Exception('type_check_exp: in proxy_array_store unexpected '
                            + repr(tup_t))
      case Call(Name('any_store'), [tup, index, value]):
        tup_t = self.type_check_exp(tup, env)
        self.check_type_equal(tup_t, AnyType(), tup)
        value_t = self.type_check_exp(value, env)
        self.check_type_equal(value_t, AnyType(), value)
        index_ty = self.type_check_exp(index, env)
        self.check_type_equal(index_ty, IntType(), index)
        return VoidType()
      case _:
        return super().type_check_exp(e, env)

