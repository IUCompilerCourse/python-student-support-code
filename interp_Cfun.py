from ast import *
from interp_Carray import InterpCarray
from utils import *
from interp_Lfun import Function, RetValue

class InterpCfun(InterpCarray):

  def apply_fun(self, fun, args, e):
      match fun:
        case Function(name, xs, blocks, env):
          old_blocks = self.blocks
          self.blocks = blocks
          new_env = {x: v for (x,v) in env.items()}
          for (x,arg) in zip(xs, args):
              new_env[x] = arg
          ret = self.interp_stmts(blocks[label_name(name + 'start')], new_env)
          self.blocks = old_blocks
          match ret:
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
      case TailCall(func, args):
        return RetValue(self.interp_exp(Call(func, args), env))
      case Return(value):
        return RetValue(self.interp_exp(value, env))
      case If(test, body, orelse):
        match self.interp_exp(test, env):
          case True:
            return self.interp_stmts(body, env)
          case False:
            return self.interp_stmts(orelse, env)
      case Goto(label):          
        return self.interp_stmts(self.blocks[label], env)
      case _:
        return super().interp_stmt(s, env)
    
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
      case CProgramDefs(defs):
        env = {}
        for d in defs:
            match d:
              case FunctionDef(name, params, blocks, dl, returns, comment):
                env[name] = Function(name, [x for (x,t) in params], blocks, env)
        self.blocks = {}
        self.apply_fun(env['main'], [], None)
      case _:
        raise Exception('interp: unexpected ' + repr(p))
    
