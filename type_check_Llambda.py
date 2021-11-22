import ast
from ast import *
from type_check_Lfun import TypeCheckLfun
from utils import *
import typing

# This type checker uses bidirectional type checking to work-around
# the lack of type annotations in Python's lambdas.

class TypeCheckLlambda(TypeCheckLfun):

  def type_check_exp(self, e, env):
    match e:
      case Name(id):
        e.has_type = env[id]
        return env[id]
      case FunRefArity(id, arity):
        return env[id]
      case Closure(arity, es):
        ts = [self.type_check_exp(e, env) for e in es]
        e.has_type = TupleType(ts)
        return e.has_type
      case Lambda(params, body):
        raise Exception('cannot synthesize a type for a lambda')
      case _:
        return super().type_check_exp(e, env)
    
  def check_exp(self, e, ty, env):
    match e:
      case Lambda(params, body):
        e.has_type = ty
        #trace('*** tc_check lambda ' + repr(ty) + '\n')
        if isinstance(params, ast.arguments):
          new_params = [a.arg for a in params.args]
          e.args = new_params
        else:
          new_params = params
        match ty:
          case FunctionType(params_t, return_t):
            new_env = {x:t for (x,t) in env.items()}
            for (p,t) in zip(new_params, params_t):
                new_env[p] = t
            self.check_exp(body, return_t, new_env)
          case Bottom():
            pass
          case _:
            raise Exception('lambda does not have type ' + str(ty))
      case Call(Name('input_int'), []):
        return int
      case Call(func, args):
        func_t = self.type_check_exp(func, env)
        match func_t:
          case FunctionType(params_t, return_t):
            for (arg, param_t) in zip(args, params_t):
                self.check_exp(arg, param_t, env)
            self.check_type_equal(return_t, ty, e)
          case _:
            raise Exception('type_check_exp: in call, unexpected ' + \
                            repr(func_t))
      case _:
        t = self.type_check_exp(e, env)
        self.check_type_equal(t, ty, e)

  def check_stmts(self, ss, return_ty, env):
    if len(ss) == 0:
      return
    #trace('*** check_stmts ' + repr(ss[0]) + '\n')
    match ss[0]:
      case FunctionDef(name, params, body, dl, returns, comment):
        #trace('*** tc_check ' + name)
        new_env = {x: t for (x,t) in env.items()}
        if isinstance(params, ast.arguments):
            new_params = [(p.arg, self.parse_type_annot(p.annotation)) for p in params.args]
            ss[0].args = new_params
            new_returns = self.parse_type_annot(returns)
            ss[0].returns = new_returns
        else:
            new_params = params
            new_returns = returns
        for (x,t) in new_params:
            new_env[x] = t
        rt = self.check_stmts(body, new_returns, new_env)
        self.check_stmts(ss[1:], return_ty, env)
      case Return(value):
        #trace('** tc_check return ' + repr(value))
        self.check_exp(value, return_ty, env)
      case Assign([Name(id)], value):
        if id in env:
          self.check_exp(value, env[id], env)
        else:
          env[id] = self.type_check_exp(value, env)
        self.check_stmts(ss[1:], return_ty, env)
      case Assign([Subscript(tup, Constant(index), Store())], value):
        tup_t = self.type_check_exp(tup, env)
        match tup_t:
          case TupleType(ts):
            self.check_exp(value, ts[index], env)
          case Bottom():
            pass
          case _:
            raise Exception('check_stmts: expected a tuple, not ' \
                            + repr(tup_t))
        self.check_stmts(ss[1:], return_ty, env)
      case AnnAssign(Name(id), ty, value, simple):
        ty_annot = self.parse_type_annot(ty)
        ss[0].annotation = ty_annot
        if id in env:
            self.check_type_equal(env[id], ty_annot)
        else:
            env[id] = ty_annot
        self.check_exp(value, ty_annot, env)
        self.check_stmts(ss[1:], return_ty, env)
      case _:
        self.type_check_stmts(ss, env)

        
  def type_check(self, p):
    #trace('*** type check Llambda')
    match p:
      case Module(body):
        env = {}
        for s in body:
            match s:
              case FunctionDef(name, params, bod, dl, returns, comment):
                if isinstance(params, ast.arguments):
                    params_t = [self.parse_type_annot(p.annotation) \
                                for p in params.args]
                else:
                    params_t = [t for (x,t) in params]
                env[name] = FunctionType(params_t, self.parse_type_annot(returns))
        self.check_stmts(body, int, env)
      case _:
        raise Exception('type_check: unexpected ' + repr(p))
