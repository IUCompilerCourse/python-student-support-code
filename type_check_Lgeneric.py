import ast
from ast import *
from type_check_Llambda import TypeCheckLlambda
from utils import *
import typing
import copy

class TypeCheckLgeneric(TypeCheckLlambda):

  def check_type_equal(self, t1, t2, e):
      match (t1, t2):
        case (AllType(ps1, ty1), AllType(ps2, ty2)):
          rename = {p2: GenericVar(p1) for (p1,p2) in zip(ps1,ps2)}
          return self.check_type_equal(ty1, self.substitute_type(ty2, rename), e)
        case (_, _):
          return super().check_type_equal(t1, t2, e)

  # TODO: check_well_formed
        
  def parse_type_annot(self, annot):
      match annot:
        case Name(id):
          if id == 'int':
            return IntType()
          elif id == 'bool':
            return BoolType()
          else:
            return GenericVar(id)
        case Subscript(Name('All'), Tuple([List(ps), ty])):
          new_ps = [p.id for p in ps]
          new_ty = self.parse_type_annot(ty)
          return AllType(new_ps, new_ty)
        case _:
          return super().parse_type_annot(annot)

  def generic_variables(self, typ) -> set[str]:
      match typ:
        case GenericVar(id):
          return {id}
        case AllType(ps, ty):
          return self.generic_variables(ty) - set(ps)
        case TupleType(ts):
          vs = set()
          for t in ts:
              vs |= self.generic_variables(t)
          return vs
        case ListType(ty):
          return self.generic_variables(ty)
        case FunctionType(ps, rt):
          vs = set()
          for t in ps:
              vs |= self.generic_variables(t)
          return vs | self.generic_variables(rt)
        case IntType():
          return set()
        case BoolType():
          return set()
        case _:
          raise Exception('generic_variables: unexpected ' + repr(typ))

  def match_types(self, param_ty, arg_ty, deduced, e):
    match (param_ty, arg_ty):
      case (GenericVar(id), _):
        if id in deduced:
            self.check_type_equal(arg_ty, deduced[id], e)
        else:
            deduced[id] = arg_ty
      case (AllType(ps, ty), AllType(arg_ps, arg_ty)):
        rename = {ap:p for (ap,p) in zip(arg_ps, ps)}
        new_arg_ty = self.substitute_type(arg_ty, rename)
        self.match_types(ty, new_arg_ty, deduced, e)
      case (TupleType(ps), TupleType(ts)):
        for (p, a) in zip(ps, ts):
          self.match_types(p, a, deduced, e)
      case (ListType(p), ListType(a)):
        self.match_types(p, a, deduced, e)
      case (FunctionType(pps, prt), FunctionType(aps, art)):
        for (pp, ap) in zip(pps, aps):
            self.match_types(pp, ap, deduced, e)
        self.match_types(prt, art, deduced, e)
      case (IntType(), IntType()):
        pass
      case (BoolType(), BoolType()):
        pass
      case _:
        raise Exception('mismatch: ' + str(param_ty) + '\n!= ' + str(arg_ty))

  def substitute_type(self, ty, var_map):
    match ty:
      case GenericVar(id):
        return var_map[id]
      case AllType(ps, ty):
        new_map = copy.deepcopy(var_map)
        for p in ps:
          new_map[p] = GenericVar(p)
        return AllType(ps, self.substitute_type(ty, new_map))
      case TupleType(ts):
        return TupleType([self.substitute_type(t, var_map) for t in ts])
      case ListType(ty):
        return ListType(self.substitute_type(ty, var_map))
      case FunctionType(pts, rt):
        return FunctionType([self.substitute_type(p, var_map) for p in pts],
                            self.substitute_type(rt, var_map))
      case IntType():
        return IntType()
      case BoolType():
        return BoolType()
      case _:
        raise Exception('substitute_type: unexpected ' + repr(ty))
    
  def type_check_exp(self, e, env):
    match e:
      case Call(Name(f), args) if f in builtin_functions:
        return super().type_check_exp(e, env)      
      case Call(func, args):
        func_t = self.type_check_exp(func, env)
        func.has_type = func_t
        match func_t:
          case AllType(ps, FunctionType(p_tys, rt)):
            for arg in args:
                arg.has_type = self.type_check_exp(arg, env)
            arg_tys = [arg.has_type for arg in args]
            deduced = {}
            for (p, a) in zip(p_tys, arg_tys):
                self.match_types(p, a, deduced, e)
            return self.substitute_type(rt, deduced)
          case _:
            return super().type_check_exp(e, env)
      case Inst(gen, type_args):
        gen_t = self.type_check_exp(gen, env)
        gen.has_type = gen_t
        match gen_t:
          case AllType(ps, ty):
            return self.substitute_type(ty, type_args)
          case _:
            raise Exception('type_check_exp: expected generic, not ' + str(gen_t))
      case _:
        return super().type_check_exp(e, env)
        
  def check_stmts(self, ss, return_ty, env):
    if len(ss) == 0:
      return
    trace('*** Lgeneric check_stmts ' + repr(ss[0]) + '\n')
    match ss[0]:
      case ImportFrom():
        # ignore for now
        return self.check_stmts(ss[1:], return_ty, env)
      case Assign([Name(id)], Call(Name('TypeVar'), args)):
        # ignore for now
        return self.check_stmts(ss[1:], return_ty, env)
      case _:
        return super().check_stmts(ss, return_ty, env)
    
  def type_check_stmts(self, ss, env):
    if len(ss) == 0:
      return
    trace('*** Lgeneric type_check_stmts ' + repr(ss[0]) + '\n')      
    match ss[0]:
      case ImportFrom():
        # ignore for now
        return self.type_check_stmts(ss[1:], env)
      case Assign([Name(id)], Call(Name('TypeVar'), args)):
        # ignore for now
        return self.type_check_stmts(ss[1:], env)
      case Pass():
        return self.type_check_stmts(ss[1:], env)
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
                    returns_t = self.parse_type_annot(returns)
                else:
                    params_t = [t for (x,t) in params]
                    returns_t = returns
                ty_params = set()
                for t in params_t:
                  ty_params |= self.generic_variables(t)
                ty = FunctionType(params_t, returns_t)
                if len(ty_params) > 0:
                    ty = AllType(list(ty_params), ty)
                env[name] = ty
        self.check_stmts(body, IntType(), env)
      case _:
        raise Exception('type_check: unexpected ' + repr(p))
        
