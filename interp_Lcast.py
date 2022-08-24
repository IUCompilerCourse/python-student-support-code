from ast import *
from interp_Lfun import Function
from interp_Llambda import InterpLlambda, ClosureTuple
from interp_Lany import InterpLany
from interp_Ldyn import Tagged
from utils import *
    
class InterpLcast(InterpLany):

  def apply_inject(self, value, source):
    return Tagged(value, self.type_to_tag(source))

  def apply_project(self, value, target):
        match value:
          case Tagged(val, tag) if self.type_to_tag(target) == tag:
            return val
          case _:
            raise Exception('apply_project, unexpected ' + repr(value))
        
  def apply_cast(self, value, source, target):
    match (source, target):
      case (AnyType(), FunctionType(ps2, rt2)):
        anyfun = FunctionType([AnyType() for p in ps2], AnyType())
        return self.apply_cast(self.apply_project(value, anyfun),
                               anyfun, target)
      case (AnyType(), TupleType(ts2)):
        anytup = TupleType([AnyType() for t1 in ts2])
        return self.apply_cast(self.apply_project(value, anytup),
                               anytup, target)
      case (AnyType(), ListType(t2)):
        anylist = ListType([AnyType() for t1 in ts2])
        return self.apply_cast(self.apply_project(value, anylist),
                               anylist, target)
      case (AnyType(), AnyType()):
        return value
      case (AnyType(), _):
        return self.apply_project(value, target)
      case (FunctionType(ps1,rt1), AnyType()):
        anyfun = FunctionType([AnyType() for p in ps1], AnyType())
        return self.apply_inject(self.apply_cast(value, source, anyfun), anyfun)
      case (TupleType(ts1), AnyType()):
        anytup = TupleType([AnyType() for t1 in ts1])
        return self.apply_inject(self.apply_cast(value, source, anytup), anytup)
      case (ListType(t1), AnyType()):
        anylist = ListType(AnyType())
        return self.apply_inject(self.apply_cast(value, source, anylist), anylist)
      case (_, AnyType()):
        return self.apply_inject(value, source)
      case (FunctionType(ps1, rt1), FunctionType(ps2, rt2)):
        params = [generate_name('x') for p in ps2]
        args = [Cast(Name(x), t2, t1)
                for (x,(t1,t2)) in zip(params, zip(ps1, ps2))]
        body = Cast(Call(ValueExp(value), args), rt1, rt2)
        return Function('cast', params, [Return(body)], {})
      case (TupleType(ts1), TupleType(ts2)):
        x = generate_name('x')
        reads = [Function('cast', [x], [Return(Cast(Name(x), t1, t2))], {})
                 for (t1,t2) in zip(ts1,ts2)]
        return ProxiedTuple(value, reads)
      case (ListType(t1), ListType(t2)):
        x = generate_name('x')
        read = Function('cast', [x], [Return(Cast(Name(x), t1, t2))], {})
        write = Function('cast', [x], [Return(Cast(Name(x), t2, t1))], {})
        return ProxiedList(value, read, write)
      case (t1, t2) if t1 == t2:
        return value
      case (t1, t2):
        raise Exception('apply_cast unexpected ' + repr(source)
                        + ' ' + repr(target))
    
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
      case ValueExp(value):
        return value
      case Cast(value, source, target):
        v = self.interp_exp(value, env)
        return self.apply_cast(v, source, target)
      case Call(Name('array_load'), [arr, index]):
        a = self.interp_exp(arr, env)
        i = self.interp_exp(index, env)
        return self.interp_getitem(a, i)
      case Call(Name('array_store'), [tup, index, value]):
        t = self.interp_exp(tup, env)
        i = self.interp_exp(index, env)
        v = self.interp_exp(value, env)
        self.interp_setitem(t, i, v)
        return None
      case Call(Name('array_len'), [tup]):
        t = self.interp_exp(tup, env)
        return self.interp_len(t)
      case _:
        return super().interp_exp(e, env)
    
