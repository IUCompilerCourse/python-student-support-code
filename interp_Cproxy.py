from ast import *
from interp_Ldyn import Tagged
from interp_Llambda import ClosureTuple
from interp_Cany import InterpCany
from utils import *

class InterpCproxy(InterpCany):

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
        case _:
          return super().type_to_tag(typ)
      
  def interp_getitem(self, aggregate, index):
    match aggregate:
      case ProxiedTuple(tup, reads):
        return self.apply_fun(reads[index],
                              [self.interp_getitem(tup, index)], None)
      case ProxiedList(lst, read, write):
        return self.apply_fun(read, [self.interp_getitem(lst, index)], None)
      case _:
        return super().interp_getitem(aggregate, index)

  def interp_setitem(self, aggregate, index, value):
    match aggregate:
      case ProxiedList(lst, read, write):
        value2 = self.apply_fun(write, [value], None)
        self.interp_setitem(lst, index, value2)
      case Tagged(agg, tag):
        self.interp_setitem(agg, index, value)
      case _:
        super().interp_setitem(aggregate, index, value)
    
  def interp_len(self, aggregate):
    match aggregate:
      case ProxiedTuple(tup, reads):
        return self.interp_len(tup)
      case ProxiedList(lst, read, write):
        return self.interp_len(lst)
      case _:
        return super().interp_len(aggregate)
    
  def interp_exp(self, e, env):
    match e:
      case TupleProxy(tup, reads, source, target):
        reads_ = self.interp_exp(reads, env)
        return ProxiedTuple(self.interp_exp(tup, env), reads__)
      case ListProxy(lst, read, write, source, target):
        read_ = self.interp_exp(read, env)
        write_ = self.interp_exp(write, env)
        return ProxiedList(self.interp_exp(lst, env), read_, write_)
      case Subscript(tup, index, Load()):
        t = self.interp_exp(tup, env)
        n = self.interp_exp(index, env)
        return self.interp_getitem(t, n)
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
          case ProxiedList(tup, reads, writes):
            return True
          case _:
            return False
      case Call(Name('proxy_array_get'), [arr, index]):
        a = self.interp_exp(arr, env)
        i = self.interp_exp(index, env)
        return self.interp_getitem(a, i)
      case Call(Name('proxy_tuple_load'), [tup, index]):
        p = self.interp_exp(tup, env)
        i = self.interp_exp(index, env)
        return self.interp_getitem(p, i)
      case Call(Name('proxy_array_load'), [tup, index]):
        p = self.interp_exp(tup, env)
        i = self.interp_exp(index, env)
        return self.interp_getitem(p, i)
      case Call(Name('proxy_array_store'), [tup, index, value]):
        p = self.interp_exp(tup, env)
        i = self.interp_exp(index, env)
        v = self.interp_exp(value, env)
        self.interp_setitem(p, i, v)
        return None
      case Call(Name('project_array'), [array]):
        return self.interp_exp(array, env)
      case Call(Name('proxy_array_len'), [tup]):
        t = self.interp_exp(tup, env)
        return self.interp_len(t)
      case Call(Name('proxy_tuple_len'), [tup]):
        t = self.interp_exp(tup, env)
        return self.interp_len(t)
      case Call(Name('project_tuple'), [tup]):
        return self.interp_exp(tup, env)
      case _:
        return super().interp_exp(e, env)
    
