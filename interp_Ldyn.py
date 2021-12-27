from ast import *
from interp_Lfun import Function
from interp_Llambda import InterpLlambda
from utils import *

@dataclass(eq=True)
class Tagged(Value):
  value : Value
  tag : str
  __match_args__ = ("value", "tag")
  def __str__(self):
    return str(self.value)

# todo: refactor the primitive operations
    
class InterpLdyn(InterpLlambda):

  def tag(self, v):
      if v is True or v is False:
          return Tagged(v, 'bool')
      elif isinstance(v, int):
          return Tagged(v, 'int')
      elif isinstance(v, Function):
          return Tagged(v, 'function')
      elif isinstance(v, list):
          return Tagged(v, 'tuple')
      elif isinstance(v, type(None)):
          return Tagged(v, 'none')
      else:
          raise Exception('tag: unexpected ' + repr(v))

  def untag(self, v, expected_tag, ast):
      match v:
        case Tagged(val, tag):
          if tag != expected_tag:
            raise Exception('expected tag ' + expected_tag \
                            + ', not ' + ' ' + repr(v))
          return val
        case _:
          raise Exception('expected Tagged value with ' + expected_tag \
                          + ', not ' + ' ' + repr(v))

  def apply_fun(self, fun, args, e):
      f = self.untag(fun, 'function', e)
      return super().apply_fun(f, args, e)
  
  def interp_exp(self, e, env):
    match e:
      # Tag the values
      case Constant(n):
        return self.tag(super().interp_exp(e, env))
      case Tuple(es, Load()):
        return self.tag(super().interp_exp(e, env))
      case Lambda(params, body):
        return self.tag(super().interp_exp(e, env))
      case Call(Name('input_int'), []):
        return self.tag(super().interp_exp(e, env))

      # Lint operations
      case BinOp(left, Add(), right):
          l = self.interp_exp(left, env); r = self.interp_exp(right, env)
          return self.tag(self.untag(l, 'int', e) + self.untag(r, 'int', e))
      case BinOp(left, Sub(), right):
          l = self.interp_exp(left, env); r = self.interp_exp(right, env)
          return self.tag(self.untag(l, 'int', e) - self.untag(r, 'int', e))
      case UnaryOp(USub(), e1):
          v = self.interp_exp(e1, env)
          return self.tag(- self.untag(v, 'int', e))

      # Lif operations
      case IfExp(test, body, orelse):
        v = self.interp_exp(test, env)
        match self.untag(v, 'bool', e):
          case True:
            return self.interp_exp(body, env)
          case False:
            return self.interp_exp(orelse, env)
      case UnaryOp(Not(), e1):
        v = self.interp_exp(e1, env)
        return self.tag(not self.untag(v, 'bool', e))
      case BoolOp(And(), values):
        left = values[0]; right = values[1]
        l = self.interp_exp(left, env)
        match self.untag(l, 'bool', e):
          case True:
            return self.interp_exp(right, env)
          case False:
            return self.tag(False)
      case BoolOp(Or(), values):
        left = values[0]; right = values[1]
        l = self.interp_exp(left, env)
        match self.untag(l, 'bool', e):
          case True:
            return True
          case False:
            return self.interp_exp(right, env)
      case Compare(left, [cmp], [right]):
        l = self.interp_exp(left, env)
        r = self.interp_exp(right, env)
        if l.tag == r.tag:
          return self.tag(self.interp_cmp(cmp)(l.value, r.value))
        else:
          raise Exception('interp Compare unexpected ' \
                          + repr(l) + ' ' + repr(r))

      # Ltup operations
      case Subscript(tup, index, Load()):
        t = self.interp_exp(tup, env)
        n = self.interp_exp(index, env)
        return self.untag(t, 'tuple', e)[self.untag(n, 'int', e)]
      case Call(Name('len'), [tup]):
        t = self.interp_exp(tup, env)
        return self.tag(len(self.untag(t, 'tuple', e)))

      case _:
        return super().interp_exp(e, env)

  def interp_stmts(self, ss, env):
    if len(ss) == 0:
      return
    match ss[0]:
    
      # Lif statements
      case If(test, body, orelse):
        v = self.interp_exp(test, env)
        match self.untag(v, 'bool', ss[0]):
          case True:
            return self.interp_stmts(body + ss[1:], env)
          case False:
            return self.interp_stmts(orelse + ss[1:], env)
        
      # Lwhile statements
      case While(test, body, []):
        while self.untag(self.interp_exp(test, env), 'bool', ss[0]):
            self.interp_stmts(body, env)
        return self.interp_stmts(ss[1:], env)
    
      # Ltup statements
      case Assign([Subscript(tup, index)], value):
        tup = self.interp_exp(tup, env)
        index = self.interp_exp(index, env)
        tup_v = self.untag(tup, 'tuple', ss[0])
        index_v = self.untag(index, 'int', ss[0])
        tup_v[index_v] = self.interp_exp(value, env)
        return self.interp_stmts(ss[1:], env)

      # override to tag the function
      case FunctionDef(name, params, bod, dl, returns, comment):
        if isinstance(params, ast.arguments):
            ps = [p.arg for p in params.args]
        else:
            ps = [x for (x,t) in params]
        env[name] = self.tag(Function(name, ps, bod, env))
        return self.interp_stmts(ss[1:], env)
        
      case _:
        return super().interp_stmts(ss, env)
    
