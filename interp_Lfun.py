from ast import *
from interp_Larray import InterpLarray
from utils import *

class Function:
    __match_args__ = ("name", "params", "body", "env")
    def __init__(self, name, params, body, env):
        self.name = name
        self.params = params
        self.body = body
        self.env = env
    def __repr__(self):
        return 'Function(' + self.name + ', ...)'

class InterpLfun(InterpLarray):

  def apply_fun(self, fun, args, e):
      match fun:
        case Function(name, xs, body, env):
          new_env = {x: v for (x,v) in env.items()}
          for (x,arg) in zip(xs, args):
              new_env[x] = arg
          return self.interp_stmts(body, new_env)
        case _:
          raise Exception('apply_fun: unexpected: ' + repr(fun))
    
  def interp_exp(self, e, env):
    match e:
      case Call(Name(f), args) if f in builtin_functions:
        return super().interp_exp(e, env)      
      case Call(func, args):
        f = self.interp_exp(func, env)
        vs = [self.interp_exp(arg, env) for arg in args]
        return self.apply_fun(f, vs, e)
      case FunRef(id, arity):
        return env[id]
      case _:
        return super().interp_exp(e, env)

  def interp_stmt(self, s, env, cont):
    match s:
      case Return(value):
        return self.interp_exp(value, env)
      case FunctionDef(name, params, bod, dl, returns, comment):
        if isinstance(params, ast.arguments):
            ps = [p.arg for p in params.args]
        else:
            ps = [x for (x,t) in params]
        env[name] = Function(name, ps, bod, env)
        return self.interp_stmts(cont, env)
      case _:
        return super().interp_stmt(s, env, cont)

  def interp(self, p):
    match p:
      case Module(ss):
        env = {}
        self.interp_stmts(ss, env)
        if 'main' in env.keys():
            self.apply_fun(env['main'], [], None)
      case _:
        raise Exception('interp: unexpected ' + repr(p))
