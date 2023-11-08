import ast
from ast import *
from type_check_Llambda import TypeCheckLlambda
from utils import *
import typing

class TypeCheckLgrad(TypeCheckLlambda):

  def parse_type_annot(self, annot):
      match annot:
        case None:
          return AnyType()
        case Name('Any'):
          return AnyType()
        case AnyType():
          return AnyType()
        case _:
          return super().parse_type_annot(annot)
    
  def check_consistent(self, t1, t2, e):
    if not self.consistent(t1, t2):
      raise Exception('error: ' + repr(t1) + ' inconsistent with ' + repr(t2) \
                      + ' in ' + repr(e))

  def consistent(self, t1, t2):
      match (t1, t2):
        case (Bottom(), _):
          return True
        case (_, Bottom()):
          return True
        case (AnyType(), _):
          return True
        case (_, AnyType()):
          return True
        case (FunctionType(ps1, rt1), FunctionType(ps2, rt2)):
          return all([self.consistent(p1, p2) for (p1,p2) in zip(ps1,ps2)]) \
              and self.consistent(rt1, rt2)
        case (TupleType(ts1), TupleType(ts2)):
          return all([self.consistent(ty1, ty2) for (ty1,ty2) in zip(ts1,ts2)])
        case (ListType(ty1), ListType(ty2)):
          return self.consistent(ty1, ty2)
        case (_, _):
          return t1 == t2

  def join_types(self, t1, t2):
      match (t1, t2):
        case (Bottom(), _):
          return t2
        case (_, Bottom()):
          return t1
        case (AnyType(), _):
          return t2
        case (_, AnyType()):
          return t1
        case (FunctionType(ps1, rt1), FunctionType(ps2, rt2)):
          return FunctionType([self.join_types(p1, p2) for (p1,p2) in zip(ps1, ps2)],
                              self.join_types(rt1,rt2))
        case (TupleType(ts1), TupleType(ts2)):
          return TupleType([self.join_types(ty1, ty2) for (ty1,ty2) in zip(ts1,ts2)])
        case (ListType(ty1), ListType(ty2)):
          return ListType(self.join_types(ty1, ty2))
        case (_, _):
          return t1
        
  def type_check_exp(self, e, env):
    match e:
      case Constant(value) if value is True or value is False:
        return BoolType()
      case Constant(None):
        return VoidType()
      # Cases for Lvar
      case Name(id):
        return env[id]
      case Constant(value) if isinstance(value, int):
        return IntType()
      case Call(Name('input_int'), []):
        return IntType()
      case Call(Name('exit'), []):
        return Bottom()
      case BinOp(left, op, right) if isinstance(op, Add) \
          or isinstance(op, Sub) or isinstance(op, Mult):
        left_type = self.type_check_exp(left, env)
        self.check_consistent(left_type, IntType(), left)
        right_type = self.type_check_exp(right, env)
        self.check_consistent(right_type, IntType(), right)
        return IntType()
      case UnaryOp(USub(), v):
        ty = self.type_check_exp(v, env)
        self.check_consistent(ty, IntType(), v)
        return IntType()
      # Cases for Lif
      case IfExp(test, body, orelse):
        test_t = self.type_check_exp(test, env)
        self.check_consistent(test_t, BoolType(), test)
        body_t = self.type_check_exp(body, env)
        orelse_t = self.type_check_exp(orelse, env)
        self.check_consistent(body_t, orelse_t, e)
        return self.join_types(body_t, orelse_t)
      case UnaryOp(Not(), v):
        ty = self.type_check_exp(v, env)
        self.check_consistent(ty, BoolType(), v)
        return BoolType()
      case BoolOp(op, values):
        left = values[0]; right = values[1]
        left_type = self.type_check_exp(left, env)
        self.check_consistent(left_type, BoolType(), left)
        right_type = self.type_check_exp(right, env)
        self.check_consistent(right_type, BoolType(), right)
        return BoolType()
      case Compare(left, [cmp], [right]) \
          if isinstance(cmp, Eq) or isinstance(cmp, NotEq):
        left_type = self.type_check_exp(left, env)
        right_type = self.type_check_exp(right, env)
        self.check_consistent(left_type, right_type, e)
        return BoolType()
      case Compare(left, [cmp], [right]) \
          if isinstance(cmp, Lt) or isinstance(cmp, LtE) \
             or isinstance(cmp, Gt) or isinstance(cmp, GtE):
        left_type = self.type_check_exp(left, env)
        self.check_consistent(left_type, IntType(), left)
        right_type = self.type_check_exp(right, env)
        self.check_consistent(right_type, IntType(), right)
        return BoolType()
      case Begin(ss, e):
        self.type_check_stmts(ss, env, None)
        return self.type_check_exp(e, env)
      # Cases for Ltup
      case Compare(left, [cmp], [right]) if isinstance(cmp, Is):
        left_type = self.type_check_exp(left, env)
        right_type = self.type_check_exp(right, env)
        self.check_consistent(left_type, right_type, e)
        return BoolType()
      case Tuple(es, Load()):
        ts = [self.type_check_exp(e, env) for e in es]
        e.has_type = TupleType(ts)
        return e.has_type
      case Subscript(tup, Constant(index), Load()) if isinstance(index,int):
        tup_ty = self.type_check_exp(tup, env)
        tup.has_type = tup_ty
        match tup_ty:
          case TupleType(ts):
            return ts[index]
          case ListType(elt_ty):
            return elt_ty
          case AnyType():
            return AnyType()
          case _:
            raise Exception('subscript expected a tuple, not ' + repr(tup_ty))
      case Subscript(tup, index, Load()):
        tup_ty = self.type_check_exp(tup, env)
        tup.has_type = tup_ty
        index_ty = self.type_check_exp(index, env)
        self.check_consistent(index_ty, IntType(), index)
        match tup_ty:
          case TupleType(ts):
            return AnyType()
          case ListType(elt_ty):
            return elt_ty
          case AnyType():
            return AnyType()
          case _:
            raise Exception('subscript a tuple, not ' + repr(tup_ty))
      case Call(Name('len'), [tup]):
        tup_t = self.type_check_exp(tup, env)
        tup.has_type = tup_t
        match tup_t:
          case TupleType(ts):
            return IntType()
          case ListType(ty):
            return IntType()
          case AnyType():
            return IntType()
          #case Bottom():
          #  return Bottom()
          case _:
            raise Exception('len expected a tuple, not ' + repr(tup_t))
      # Cases for Larray
      case ast.List(es, Load()):
        ts = [self.type_check_exp(e, env) for e in es]
        elt_ty = ts[0]
        for (ty, elt) in zip(ts, es):
            self.check_consistent(elt_ty, ty, elt)
            elt_ty = self.join_types(elt_ty, ty)
        e.has_type = ListType(elt_ty)
        return e.has_type

      case Call(Name('array_len'), [tup]):
        tup_t = self.type_check_exp(tup, env)
        tup.has_type = tup_t
        match tup_t:
          case ListType(ty):
            return IntType()
          case Bottom():
            return Bottom()
          case AnyType():
            return IntType()
          case _:
            raise Exception('array_len: unexpected ' + repr(tup_t))
      case Call(Name('array_load'), [lst, index]):
        lst_ty = self.type_check_exp(lst, env)
        index_ty = self.type_check_exp(index, env)
        self.check_consistent(index_ty, IntType(), index)
        match lst_ty:
          case ListType(ty):
            return ty
          case AnyType():
            return AnyType()
          case _:
            raise Exception('array_load: unexpected ' + repr(lst_ty))
      case Call(Name('array_store'), [tup, index, value]):
        tup_t = self.type_check_exp(tup, env)
        value_t = self.type_check_exp(value, env)
        index_ty = self.type_check_exp(index, env)
        self.check_consistent(index_ty, IntType(), index)
        match tup_t:
          case ListType(ty):
            self.check_consistent(ty, value_t, e)
            return VoidType()
          case Bottom():
            return VoidType()
          case AnyType():
            return VoidType()
          case _:
            raise Exception('type_check_exp: unexpected ' + repr(tup_t))
      
      # Cases for Llambda
      case Lambda(params, body):
        self.check_exp(e, AnyType(), env)
        return AnyType()
      case Call(Name('arity'), [func]):
        func_t = self.type_check_exp(func, env)
        match func_t:
          case FunctionType(params_t, return_t):
            return IntType()
          case AnyType():
            return IntType()
          case _:
            raise Exception('type_check_exp: in arity, unexpected ' + \
                            repr(func_t))
          
      # primitives introduced by the resolve pass
      case Call(Name('any_load'), [tup, index]):
        self.check_exp(tup, AnyType(), env)
        self.check_exp(index, IntType(), env)
        return AnyType()
      case Call(Name('any_store'), [tup, index, value]):
        self.check_exp(tup, AnyType(), env)
        self.type_check_exp(value, env)
        self.check_exp(index, IntType(), env)
        return VoidType()
      case Call(Name('any_len'), [tup]):
        self.check_exp(tup, AnyType(), env)
        return IntType()
      
      # Cases for Lfun (last because the below Call pattern is general)
      case FunRef(id, arity):
        return env[id]
      case Call(func, args):
        func_t = self.type_check_exp(func, env)
        match func_t:
          case FunctionType(params_t, return_t):
            for (arg, param_t) in zip(args, params_t):
                self.check_exp(arg, param_t, env)
            # for (arg_t, param_t) in zip(args_t, params_t):
            #     self.check_consistent(param_t, arg_t, e)
            return return_t
          case AnyType():
            args_t = [self.type_check_exp(arg, env) for arg in args]
            anys = [AnyType() for _ in args_t]
            fun_ty = FunctionType(anys, AnyType())
            return AnyType()
          case _:
            raise Exception('type_check_exp: in call, unexpected ' + \
                            repr(func_t))
      case _:
        raise Exception('type_check_exp: unexpected ' + repr(e))
    
  def check_exp(self, e, ty, env):
    match e:
      case Lambda(params, body):
        trace('check_exp: ' + str(e) + '\nexpected type: ' + str(ty))
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
            e.has_type = ty
          case AnyType():
            new_env = {x:t for (x,t) in env.items()}
            for p in new_params:
                new_env[p] = AnyType()
            e.has_type = FunctionType([AnyType() for _ in new_params], AnyType())
          case Bottom():
            pass
          case _:
            raise Exception('lambda does not have type ' + str(ty))

      case _:
        e_ty = self.type_check_exp(e, env)
        self.check_consistent(e_ty, ty, e)
      
  def type_check_stmt(self, s, env, return_type):
    match s:
      # Cases in Lvar
      case Assign([Name(id)], value):
        value_ty = self.type_check_exp(value, env)
        if id in env:
          self.check_consistent(env[id], value_ty, value)
        else:
          env[id] = value_ty
      case Expr(Call(Name('print'), [arg])):
        arg_ty = self.type_check_exp(arg, env)
        self.check_consistent(arg_ty, IntType(), arg)
      case Expr(value):
        value_ty = self.type_check_exp(value, env)
      # Cases in Lif
      case If(test, body, orelse):
        test_ty = self.type_check_exp(test, env)
        self.check_consistent(BoolType(), test_ty, test)
        body_ty = self.type_check_stmts(body, env, return_type)
        orelse_ty = self.type_check_stmts(orelse, env, return_type)
        self.check_consistent(body_ty, orelse_ty, s)
      # Cases in Lwhile
      case While(test, body, []):
        test_t = self.type_check_exp(test, env)
        self.check_consistent(BoolType(), test_t, test)
        self.type_check_stmts(body, env, return_type)
      # Cases in Ltup and Larray
      case Assign([Subscript(tup, index, Store())], value):
        tup_t = self.type_check_exp(tup, env)
        tup.has_type = tup_t
        value_t = self.type_check_exp(value, env)
        index_ty = self.type_check_exp(index, env)
        self.check_consistent(index_ty, IntType(), index)
        match tup_t:
          case TupleType(ts):
            match index:
              case Constant(i):
                self.check_consistent(ts[i], value_t, s)
              case _:
                raise Exception('subscript required constant integer index')
          case ListType(ty):
            self.check_consistent(ty, value_t, s)
          case AnyType():
            pass
          case Bottom():
            pass
          case _:
            raise Exception('type_check_stmts: expected a list or tuple, not ' \
                            + repr(tup_t))
      # Cases in Lfun
      case FunctionDef(name, params, body, dl, returns, comment):
        if isinstance(params, ast.arguments):
            new_params = [(p.arg, self.parse_type_annot(p.annotation)) \
                          for p in params.args]
            s.args = new_params
            new_returns = self.parse_type_annot(returns)
            s.returns = new_returns
        else:
            new_params = params
            new_returns = returns
        new_env = {x: t for (x,t) in env.items()}
        for (x,t) in new_params:
            new_env[x] = t
        self.type_check_stmts(body, new_env, new_returns)
      case Return(value):
        self.check_exp(value, return_type, env)
      # Cases in Llambda
      case AnnAssign(v, type_annot, value, simple) if isinstance(v, Name):
        ty_annot = self.parse_type_annot(type_annot)
        s.annotation = ty_annot
        if v.id in env:
            self.check_consistent(env[v.id], ty_annot)
        else:
            env[v.id] = ty_annot
        v.has_type = env[v.id]
        self.check_exp(value, ty_annot, env)
      case _:
        raise Exception('type_check_stmt: unexpected ' + repr(s))

  def type_check_stmts(self, ss, env, return_type):
    for s in ss:
      self.type_check_stmt(s, env, return_type)
  
  def check_stmts(self, ss, return_ty, env):
    for s in ss:
      self.type_check_stmt(s, env, return_ty)
