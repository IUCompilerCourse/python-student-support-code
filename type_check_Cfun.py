from ast import *
from utils import *
from type_check_Ctup import check_type_equal, TypeCheckCtup
import copy

class TypeCheckCfun(TypeCheckCtup):
    
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
          case Bottom():
            return Bottom()
          case _:
            raise Exception('type_check_exp: in call, unexpected ' + \
                            repr(func_t))
      case _:
        return super().type_check_exp(e, env)

  def type_check_def(self, d, env):
    match d:
      case FunctionDef(name, params, blocks, dl, returns, comment):
        new_env = {x: t for (x,t) in env.items()}
        for p in params.args:
            new_env[p.arg] = self.parse_type_annot(p.annotation)
        while True:
            old_env = copy.deepcopy(new_env)
            for (l,ss) in blocks.items():
                self.type_check_stmts(ss, new_env)
            if new_env == old_env:
                break
        # todo check return type
        d.var_types = new_env
        # trace('type_check_Cfun var_types for ' + name)
        # trace(d.var_types)
      case _:
        raise Exception('type_check_def: unexpected ' + repr(ss[0]))

  def type_check_stmts(self, ss, env):
    if len(ss) == 0:
      return
    match ss[0]:
      case Return(value):
        return self.type_check_exp(value, env)
      case _:
        return super().type_check_stmts(ss, env)
    
  def type_check(self, p):
    match p:
      case CProgramDefs(defs):
        env = {}
        for d in defs:
            match d:
              case FunctionDef(name, params, bod, dl, returns, comment):
                params_t = [self. parse_type_annot(p.annotation) \
                            for p in params.args]
                env[name] = FunctionType(params_t,
                                         self.parse_type_annot(returns))
        for d in defs:
            self.type_check_def(d, env)
      case _:
        raise Exception('type_check: unexpected ' + repr(p))

