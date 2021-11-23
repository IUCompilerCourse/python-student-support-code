from ast import *
from utils import CProgram, Goto, trace, Bottom, Let
import copy

class TypeCheckCif:

  def check_type_equal(self, t1, t2, e):
    if t1 == Bottom() or t2 == Bottom():
      pass
    elif t1 != t2:
      raise Exception('error: ' + repr(t1) + ' != ' + repr(t2) \
                      + ' in ' + repr(e))

  def type_check_atm(self, e, env):
    match e:
      case Name(id):
        return env.get(id, Bottom())
      case Constant(value) if isinstance(value, bool):
        return bool
      case Constant(value) if isinstance(value, int):
        return int
      case _:
        raise Exception('error in type_check_atm, unexpected ' + repr(e))
     
  def type_check_exp(self, e, env):
    match e:
      case Name(id):
        return self.type_check_atm(e, env)
      case Constant(value):
        return self.type_check_atm(e, env)
      case IfExp(test, body, orelse):
        test_t = self.type_check_exp(test, env)
        self.check_type_equal(bool, test_t, test)
        body_t = self.type_check_exp(body, env)
        orelse_t = self.type_check_exp(orelse, env)
        self.check_type_equal(body_t, orelse_t, e)
        return body_t
      case BinOp(left, op, right) if isinstance(op, Add) or isinstance(op, Sub):
        l = self.type_check_atm(left, env)
        self.check_type_equal(l, int, e)
        r = self.type_check_atm(right, env)
        self.check_type_equal(r, int, e)
        return int
      case UnaryOp(USub(), v):
        t = self.type_check_atm(v, env)
        self.check_type_equal(t, int, e)
        return int
      case UnaryOp(Not(), v):
        t = self.type_check_exp(v, env)
        self.check_type_equal(t, bool, e)
        return bool 
      case Compare(left, [cmp], [right]) if isinstance(cmp, Eq) or isinstance(cmp, NotEq):
        l = self.type_check_atm(left, env)
        r = self.type_check_atm(right, env)
        self.check_type_equal(l, r, e)
        return bool
      case Compare(left, [cmp], [right]):
        l = self.type_check_atm(left, env)
        self.check_type_equal(l, int, left)
        r = self.type_check_atm(right, env)
        self.check_type_equal(r, int, right)
        return bool
      case Call(Name('input_int'), []):
        return int
      case Let(Name(x), rhs, body):
        t = self.type_check_exp(rhs, env)
        new_env = dict(env)
        new_env[x] = t
        return self.type_check_exp(body, new_env)
      case _:
        raise Exception('error in type_check_exp, unexpected ' + repr(e))

  def type_check_stmts(self, ss, env):
      for s in ss:
          self.type_check_stmt(s, env)
      
  def type_check_stmt(self, s, env):
    match s:      
      case Assign([lhs], value):
        t = self.type_check_exp(value, env)
        if lhs.id in env:
          self.check_type_equal(env.get(lhs.id, Bottom()), t, s)
        else:
          env[lhs.id] = t
      case Expr(Call(Name('print'), [arg])):
        t = self.type_check_exp(arg, env)
        self.check_type_equal(t, int, s)
      case Expr(value):
        self.type_check_exp(value, env)
      case If(Compare(left, [cmp], [right]), body, orelse):
        left_t = self.type_check_atm(left, env)
        right_t = self.type_check_atm(right, env)
        self.check_type_equal(left_t, right_t, s) # not quite strict enough
        self.type_check_stmts(body, env)
        self.type_check_stmts(orelse, env)
      case Goto(label):
        pass
      case Return(value):
        value_t = self.type_check_exp(value, env)
      case _:
        raise Exception('error in type_check_stmt, unexpected' + repr(s))
    
  def type_check(self, p):
    match p:
      case CProgram(body):
          env = {}
          while True:
              old_env = copy.deepcopy(env)
              for (l, ss) in body.items():
                  self.type_check_stmts(ss, env)
              if env == old_env:
                  break
          p.var_types = env
      case _:
        raise Exception('error in type_check, unexpected ' + repr(p))
