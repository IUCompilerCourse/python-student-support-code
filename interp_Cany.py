from ast import *
from interp_Ldyn import Tagged
from interp_Llambda import ClosureTuple
from interp_Clambda import InterpClambda
from utils import *

class InterpCany(InterpClambda):

  def interp_exp(self, e, env):
    match e:
      case Call(Name('make_any'), [value, tag]):
        v = self.interp_exp(value, env)
        t = self.interp_exp(tag, env)
        return Tagged(v, t)
      case Call(Name('exit'), []):
        trace('exiting!')
        exit(0)
      case TagOf(value):
        v = self.interp_exp(value, env)
        match v:
          case Tagged(val, tag):
            return tag
          case _:
            raise Exception('interp TagOf unexpected ' + repr(v))
      case ValueOf(value, typ):
        v = self.interp_exp(value, env)
        match v:
          case Tagged(val, tag):
            return val
          case _:
            raise Exception('interp ValueOf unexpected ' + repr(v))
      case Call(Name('any_tuple_load'), [tup, index]):
        tv = self.interp_exp(tup, env)
        n = self.interp_exp(index, env)
        match tv:
          case Tagged(v, tag):
            return v[n]
          case _:
            raise Exception('interp any_tuple_load unexpected ' + repr(tv))
      case Call(Name('any_tuple_store'), [tup, index, value]):
        tv = self.interp_exp(tup, env)
        n = self.interp_exp(index, env)
        val = self.interp_exp(value, env)
        match tv:
          case Tagged(v, tag):
            v[n] = val
            return None # ??
          case _:
            raise Exception('interp any_tuple_load unexpected ' + repr(tv))
      case Call(Name('any_len'), [value]):
        v = self.interp_exp(value, env)
        match v:
          case Tagged(value, tag):
            return len(value)
          case _:
            raise Exception('interp any_len unexpected ' + repr(v))
      case _:
        return super().interp_exp(e, env)
