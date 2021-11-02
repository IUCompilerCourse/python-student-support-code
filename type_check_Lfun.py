from ast import *
from type_check_Lvar import check_type_equal
from type_check_Ltup import TypeCheckLtup
from utils import *
import typing

class TypeCheckLfun(TypeCheckLtup):

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
        case _:
            raise Exception('parse_type_annot: unexpected ' + repr(annot))
    
  def type_check_exp(self, e, env):
    match e:
      case FunRef(id):
        return env[id]
      case Call(Name('input_int'), []):
        return super().type_check_exp(e, env)      
      case Call(func, args):
        func_t = self.type_check_exp(func, env)
        args_t = [self.type_check_exp(arg, env) for arg in args]
        match func_t:
          case FunctionType(params_t, return_t):
            for (arg_t, param_t) in zip(args_t, params_t):
                check_type_equal(param_t, arg_t, e)
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
        for p in params.args:
            new_env[p.arg] = self.parse_type_annot(p.annotation)
        rt = self.type_check_stmts(body, new_env)
        check_type_equal(self.parse_type_annot(returns), rt, ss[0])
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
                params_t = [self. parse_type_annot(p.annotation) \
                            for p in params.args]
                env[name] = FunctionType(params_t,
                                         self.parse_type_annot(returns))
        self.type_check_stmts(body, env)
      case _:
        raise Exception('type_check: unexpected ' + repr(p))
