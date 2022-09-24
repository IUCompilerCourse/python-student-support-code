from ast import *
from interp_Carray import InterpCarray
from utils import *
from interp_Lfun import Function

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
          return ret
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
      case TailCall(func, args):
        return self.interp_exp(Call(func, args), env)
      case _:
        return super().interp_stmt(s, env, cont)
    
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
    
