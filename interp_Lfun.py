from dataclasses import dataclass
from ast import *
from interp_Larray import InterpLarray
from utils import *


# The return statement returns a RetValue(), and other
# compound statements immediately transmit this to their parent.
# All other statements continue to return None
@dataclass
class RetValue():
  v:any

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
          match self.interp_stmts(body, new_env):
             case RetValue(v):
               return v
             case None:
               return None
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

  def interp_stmt(self, s, env):
    match s:
      case FunctionDef(name, params, bod, dl, returns, comment):
        if isinstance(params, ast.arguments):
            ps = [p.arg for p in params.args]
        else:
            ps = [x for (x,t) in params]
        env[name] = Function(name, ps, bod, env)
      case Return(value):
        return RetValue(self.interp_exp(value, env))
      case If(test, body, orelse):       # revised to cover possibility of early return 
        match self.interp_exp(test, env):
          case True:
            return self.interp_stmts(body, env)
          case False:
            return self.interp_stmts(orelse, env)
      case While(test, body, []):        # ditto 
        while self.interp_exp(test, env):
           r = self.interp_stmts(body, env)
           match r:
             case RetValue(_):
               return r
             case _:
               pass
      case _:
        return super().interp_stmt(s, env)

  # revised to cover possibility of early return
  def interp_stmts(self, ss, env):
    for s in ss:
      r = self.interp_stmt(s,env)
      match r:
        case RetValue(_):
          return r
        case _:
          pass
      
  def interp(self, p):
    match p:
      case Module(ss):
        env = {}
        self.interp_stmts(ss, env)
        #trace('interp global env: ' + repr(env))
        if 'main' in env.keys():
            self.apply_fun(env['main'], [], None)
      case _:
        raise Exception('interp: unexpected ' + repr(p))
