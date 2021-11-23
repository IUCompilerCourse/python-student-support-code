import ast
from ast import *
from type_check_Ltup import TypeCheckLtup
from utils import *
import typing

class TypeCheckLfun(TypeCheckLtup):

  def check_type_equal(self, t1, t2, e):
    if t1 == Bottom() or t2 == Bottom():
      return
    match t1:
      case FunctionType(ps1, rt1):
        match t2:
          case FunctionType(ps2, rt2):
            for (p1,p2) in zip(ps1, ps2):
              self.check_type_equal(p1, p2, e)
              self.check_type_equal(rt1, rt2, e)
          case _:
            raise Exception('error: ' + repr(t1) + ' != ' + repr(t2) \
                            + ' in ' + repr(e))
      case _:
        super().check_type_equal(t1, t2, e)
  
  def parse_type_annot(self, annot):
      match annot:
        case Name(id):
          if id == 'int':
            return int
          elif id == 'bool':
            return bool
          else:
            raise Exception('parse_type_annot: unexpected ' + repr(annot))
        case TupleType(ts):
          return TupleType([self.parse_type_annot(t) for t in ts])
        case FunctionType(ps, rt):
          return FunctionType([self.parse_type_annot(t) for t in ps],
                              self.parse_type_annot(rt))
        case Subscript(Name('Callable'), Tuple([ps, rt])):
          return FunctionType([self.parse_type_annot(t) for t in ps.elts],
                              self.parse_type_annot(rt))
        case Subscript(Name('tuple'), Tuple(ts)):
          return TupleType([self.parse_type_annot(t) for t in ts])
        case t if t == int or t == bool or t == type(None):
          return annot
        case Constant(None):
          return type(None)
        case _:
            raise Exception('parse_type_annot: unexpected ' + repr(annot))
    
  def type_check_exp(self, e, env):
    match e:
      case FunRef(id):
        return env[id]
      case Call(Name('input_int'), []):
        return super().type_check_exp(e, env)      
      case Call(Name('len'), [tup]):
        return super().type_check_exp(e, env)      
      case Call(func, args):
        func_t = self.type_check_exp(func, env)
        args_t = [self.type_check_exp(arg, env) for arg in args]
        match func_t:
          case FunctionType(params_t, return_t):
            for (arg_t, param_t) in zip(args_t, params_t):
                self.check_type_equal(param_t, arg_t, e)
            return return_t
          case _:
            raise Exception('type_check_exp: in call, unexpected ' + \
                            repr(func_t))
      case _:
        return super().type_check_exp(e, env)

  def type_check_stmts(self, ss, env):
    if len(ss) == 0:
      return
    match ss[0]:
      case FunctionDef(name, params, body, dl, returns, comment):
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
        rt = self.type_check_stmts(body, new_env)
        self.check_type_equal(new_returns, rt, ss[0])
        return self.type_check_stmts(ss[1:], env)
      case Return(value):
        return self.type_check_exp(value, env)
      case _:
        return super().type_check_stmts(ss, env)

  def type_check(self, p):
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
        self.type_check_stmts(body, env)
      case _:
        raise Exception('type_check: unexpected ' + repr(p))
