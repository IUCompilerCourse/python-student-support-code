from ast import *
from type_check_Lvar import TypeCheckLvar, check_type_equal
from utils import *

class TypeCheckLif(TypeCheckLvar):
          
  def type_check_exp(self, e, env):
    match e:
      case Constant(value) if isinstance(value, bool):
        return bool
      case IfExp(test, body, orelse):
        test_t = self.type_check_exp(test, env)
        check_type_equal(bool, test_t, test)
        body_t = self.type_check_exp(body, env)
        orelse_t = self.type_check_exp(orelse, env)
        check_type_equal(body_t, orelse_t, e)
        return body_t
      case BinOp(left, Sub(), right):
        l = self.type_check_exp(left, env)
        check_type_equal(l, int, left)
        r = self.type_check_exp(right, env)
        check_type_equal(r, int, right)
        return int
      case UnaryOp(Not(), v):
        t = self.type_check_exp(v, env)
        check_type_equal(t, bool, v)
        return bool 
      case BoolOp(op, values):
        left = values[0]; right = values[1]
        l = self.type_check_exp(left, env)
        check_type_equal(l, bool, left)
        r = self.type_check_exp(right, env)
        check_type_equal(r, bool, right)
        return bool
      case Compare(left, [cmp], [right]) if isinstance(cmp, Eq) or isinstance(cmp, NotEq):
        l = self.type_check_exp(left, env)
        r = self.type_check_exp(right, env)
        check_type_equal(l, r, e)
        return bool
      case Compare(left, [cmp], [right]):
        l = self.type_check_exp(left, env)
        check_type_equal(l, int, left)
        r = self.type_check_exp(right, env)
        check_type_equal(r, int, right)
        return bool
      case Let(Name(x), rhs, body):
        t = self.type_check_exp(rhs, env)
        new_env = dict(env); new_env[x] = t
        return self.type_check_exp(body, new_env)
      case _:
        return super().type_check_exp(e, env)

  def type_check_stmts(self, ss, env):
    if len(ss) == 0:
      return
    match ss[0]:
      case If(test, body, orelse):
        test_t = self.type_check_exp(test, env)
        check_type_equal(bool, test_t, test)
        body_t = self.type_check_stmts(body, env)
        orelse_t = self.type_check_stmts(orelse, env)
        check_type_equal(body_t, orelse_t, ss[0])
        if len(ss) > 1:
          return self.type_check_stmts(ss[1:], env)
        else: # this 'if' statement is in tail position
          return body_t
      case _:
        return super().type_check_stmts(ss, env)
