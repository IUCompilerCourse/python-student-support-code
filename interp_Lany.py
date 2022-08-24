from ast import *
from interp_Lfun import Function
from interp_Llambda import InterpLlambda, ClosureTuple
from interp_Ldyn import Tagged
from utils import *
    
class InterpLany(InterpLlambda):

  def type_to_tag(self, typ):
      match typ:
        case FunctionType(params, rt):
          return 'function'
        case TupleType(fields):
          return 'tuple'
        case ListType(elt_ty):
          return 'tuple'
        case t if t == int:
          return 'int'
        case t if t == bool:
          return 'bool'
        case IntType():
          return 'int'
        case BoolType():
          return 'int'
        case _:
          raise Exception('type_to_tag unexpected ' + repr(typ))

  def arity(self, v):
    match v:
      case Function(name, params, body, env):
        return len(params)
      case ClosureTuple(args, arity):
        return arity
      case _:
        raise Exception('Lany arity unexpected ' + repr(v))

  # hook to be overridden
  def interp_getitem(self, aggregate, index):
      return aggregate[index]

  # hook to be overridden
  def interp_setitem(self, aggregate, index, value):
      aggregate[index] = value
    
  # hook to be overridden    
  def interp_len(self, aggregate):
      return len(aggregate)
    
  def interp_exp(self, e, env):
    match e:
      case Inject(value, typ):
        v = self.interp_exp(value, env)
        return Tagged(v, self.type_to_tag(typ))
      case Project(value, typ):
        v = self.interp_exp(value, env)
        match v:
          case Tagged(val, tag) if self.type_to_tag(typ) == tag:
            return val
          case _:
            raise Exception('interp project to ' + repr(typ) \
                            + '  unexpected ' + repr(v))
      case Call(Name(atl), [tup, index]) \
          if atl == 'any_load' or atl == 'any_load_unsafe':
        tv = self.interp_exp(tup, env)
        n = self.interp_exp(index, env)
        match tv:
          case Tagged(v, tag):
            return self.interp_getitem(v, n)
          case _:
            raise Exception('interp any_load unexpected ' + repr(tv))
      case Call(Name(ats), [tup, index, value]) \
        if ats == 'any_store' or ats == 'any_store_unsafe':
        tv = self.interp_exp(tup, env)
        n = self.interp_exp(index, env)
        val = self.interp_exp(value, env)
        match tv:
          case Tagged(v, tag):
            self.interp_setitem(v, n, val)
            return None
          case _:
            raise Exception('interp any_store unexpected ' + repr(tv))
      case Subscript(tup, index, Load()):
        t = self.interp_exp(tup, env)
        n = self.interp_exp(index, env)
        return self.interp_getitem(t, n)
      case Call(Name('any_len'), [value]):
        v = self.interp_exp(value, env)
        match v:
          case Tagged(value, tag):
            return self.interp_len(value)
          case _:
            raise Exception('interp any_len unexpected ' + repr(v))
      case Call(Name('make_any'), [value, tag]):
        v = self.interp_exp(value, env)
        t = self.interp_exp(tag, env)
        return Tagged(v, t)
      case Call(Name('arity'), [fun]):
        f = self.interp_exp(fun, env)
        return self.arity(f)
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
      case AnnLambda(params, returns, body):
        return Function('lambda', [x for (x,t) in params], [Return(body)], env)
      case _:
        return super().interp_exp(e, env)
