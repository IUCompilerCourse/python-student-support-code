from ast import *
from interp_Lfun import Function
from interp_Llambda import InterpLlambda, ClosureTuple
from interp_Ldyn import Tagged
from interp_Lcast import InterpLcast
from utils import *
    
class InterpLproxy(InterpLcast):

  def apply_fun(self, fun, args, e):
      match fun:
        case ClosureTuple(elts, arity):
          return self.apply_fun(elts[0], [elts] + args, e)
        case _:
          return super().apply_fun(fun, args, e)
      
  def type_to_tag(self, typ):
      match typ:
        case ProxyOrTupleType(elt_types):
          return 'tuple'
        case ProxyOrListType(elt_type):
          return 'tuple' # ?
        case ListType(elt_type): # move to different file?
          return 'tuple'
        case _:
          return super().type_to_tag(typ)
      
  def interp_exp(self, e, env):
    match e:
      case RawTuple(es):
        return [self.interp_exp(e, env) for e in es]
      case TupleProxy(tup, reads, source, target):
        reads_ = self.interp_exp(reads, env)
        return ProxiedTuple(self.interp_exp(tup, env), reads_)
      case ListProxy(lst, read, write, source, target):
        read_ = self.interp_exp(read, env)
        write_ = self.interp_exp(write, env)
        return ProxiedList(self.interp_exp(lst, env), read_, write_)
      case InjectTupleProxy(proxy, typ):
        p = self.interp_exp(proxy, env)
        return ProxiedTuple(p[0], p[1])
      case InjectTuple(tup):
        return self.interp_exp(tup, env)
      case InjectListProxy(proxy, typ):
        p = self.interp_exp(proxy, env)
        return ProxiedList(p[0], p[1], p[2])
      case InjectList(tup):
        return self.interp_exp(tup, env)
      case Call(Name('is_tuple_proxy'), [arg]):
        p = self.interp_exp(arg, env)
        match p:
          case ProxiedTuple(tup, reads):
            return True
          case _:
            return False
      case Call(Name('is_array_proxy'), [arg]):
        p = self.interp_exp(arg, env)
        match p:
          case ProxiedList(lst, read, write):
            return True
          case _:
            return False
      case Call(Name('proxy_tuple_load'), [tup, index]):
        p = self.interp_exp(tup, env)
        i = self.interp_exp(index, env)
        return self.interp_getitem(p, i)
      case Call(Name('proxy_tuple_len'), [tup]):
        t = self.interp_exp(tup, env)
        return self.interp_len(t)
      case Call(Name('proxy_array_len'), [tup]):
        t = self.interp_exp(tup, env)
        return self.interp_len(t)
      case Call(Name('proxy_array_load'), [arr, index]):
        a = self.interp_exp(arr, env)
        i = self.interp_exp(index, env)
        return self.interp_getitem(a, i)
      case Call(Name('proxy_array_store'), [arr, index, value]):
        a = self.interp_exp(arr, env)
        i = self.interp_exp(index, env)
        v = self.interp_exp(value, env)
        self.interp_setitem(a, i, v)
        return None
      case Call(Name('project_array'), [array]):
        return self.interp_exp(array, env)
      case Call(Name('project_tuple'), [tup]):
        return self.interp_exp(tup, env)
      case _:
        return super().interp_exp(e, env)
    
  def interp_stmt(self, s, env):
    match s:
      case Assign([Call(Name('any_load'), [tup, index])], value):
        t = self.interp_exp(tup, env)
        i = self.interp_exp(index, env)
        v = self.interp_exp(value, env)
        self.interp_setitem(t, i, v)
      case _:
        return super().interp_stmt(s, env)
