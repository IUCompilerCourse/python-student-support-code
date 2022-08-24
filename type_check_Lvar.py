from ast import *
from utils import IntType

class TypeCheckLvar:
          
  def check_type_equal(self, t1, t2, e):
    if t1 != t2:
      raise Exception('error: ' + repr(t1) + ' != ' + repr(t2) \
                      + ' in ' + repr(e))

  def type_check_exp(self, e, env):
    match e:
      case BinOp(left, Add(), right):
        l = self.type_check_exp(left, env)
        self.check_type_equal(l, IntType(), left)
        r = self.type_check_exp(right, env)
        self.check_type_equal(r, IntType(), right)
        return IntType()
      case BinOp(left, Sub(), right):
        l = self.type_check_exp(left, env)
        self.check_type_equal(l, IntType(), left)
        r = self.type_check_exp(right, env)
        self.check_type_equal(r, IntType(), right)
        return IntType()
      case UnaryOp(USub(), v):
        t = self.type_check_exp(v, env)
        self.check_type_equal(t, IntType(), v)
        return IntType()
      case Name(id):
        return env[id]
      case Constant(value) if isinstance(value, int):
        return IntType()
      case Call(Name('input_int'), []):
        return IntType()
      case _:
        raise Exception('type_check_exp: unexpected ' + repr(e))

  def type_check_stmts(self, ss, env):
    if len(ss) == 0:
      return
    match ss[0]:
      case Assign([Name(id)], value):
        t = self.type_check_exp(value, env)
        if id in env:
          self.check_type_equal(env[id], t, value)
        else:
          env[id] = t
        return self.type_check_stmts(ss[1:], env)
      case Expr(Call(Name('print'), [arg])):
        t = self.type_check_exp(arg, env)
        self.check_type_equal(t, IntType(), arg)
        return self.type_check_stmts(ss[1:], env)
      case Expr(value):
        self.type_check_exp(value, env)
        return self.type_check_stmts(ss[1:], env)
      case _:
        raise Exception('type_check_stmts: unexpected ' + repr(ss))

  def type_check(self, p):
    match p:
      case Module(body):
        self.type_check_stmts(body, {})
