from ast import *
from utils import CProgram, Goto, trace, Bottom, IntType, BoolType, Begin
import copy

class TypeCheckCif:

  def check_type_equal(self, t1, t2, e):
    if t1 == Bottom() or t2 == Bottom():
      pass
    elif t1 != t2:
      raise Exception('error: ' + repr(t1) + ' != ' + repr(t2) \
                      + ' in ' + repr(e))

  def combine_types(self, t1, t2):
    match (t1, t2):
      case (Bottom(), _):
        return t2
      case (_, Bottom()):
        return t1
      case _:
        return t1
    
  def type_check_atm(self, e, env):
    match e:
      case Name(id):
        t = env.get(id, Bottom())
        env[id] = t    # make sure this gets into the environment for later definedness checking
        return t
      case Constant(value) if isinstance(value, bool):
        return BoolType()
      case Constant(value) if isinstance(value, int):
        return IntType()
      case _:
        raise Exception('error in type_check_atm, unexpected ' + repr(e))
     
  def type_check_exp(self, e, env):
    match e:
      case Name(id):
        return self.type_check_atm(e, env)
      case Constant(value):
        return self.type_check_atm(e, env)
      case BinOp(left, op, right) if isinstance(op, Add) or isinstance(op, Sub):
        l = self.type_check_atm(left, env)
        self.check_type_equal(l, IntType(), e)
        r = self.type_check_atm(right, env)
        self.check_type_equal(r, IntType(), e)
        return IntType()
      case UnaryOp(USub(), v):
        t = self.type_check_atm(v, env)
        self.check_type_equal(t, IntType(), e)
        return IntType()
      case UnaryOp(Not(), v):
        t = self.type_check_exp(v, env)
        self.check_type_equal(t, BoolType(), e)
        return BoolType() 
      case Compare(left, [cmp], [right]) if isinstance(cmp, Eq) \
                                         or isinstance(cmp, NotEq):
        l = self.type_check_atm(left, env)
        r = self.type_check_atm(right, env)
        self.check_type_equal(l, r, e)
        return BoolType()
      case Compare(left, [cmp], [right]):
        l = self.type_check_atm(left, env)
        self.check_type_equal(l, IntType(), left)
        r = self.type_check_atm(right, env)
        self.check_type_equal(r, IntType(), right)
        return BoolType()
      case Call(Name('input_int'), []):
        return IntType()
      case Begin(ss, e):
        self.type_check_stmts(ss, env)
        return self.type_check_exp(e, env)
      case _:
        raise Exception('error in type_check_exp, unexpected ' + repr(e))

  def type_check_stmts(self, ss, env):
      for s in ss:
          self.type_check_stmt(s, env)
      
  def type_check_stmt(self, s, env):
    match s:      
      case Assign([lhs], value):
        t = self.type_check_exp(value, env)
        lhs_ty = env.get(lhs.id, Bottom())
        self.check_type_equal(lhs_ty, t, s)
        env[lhs.id] = self.combine_types(t, lhs_ty)
      case Expr(Call(Name('print'), [arg])):
        t = self.type_check_exp(arg, env)
        self.check_type_equal(t, IntType(), s)
      case Expr(value):
        self.type_check_exp(value, env)
      case _:
        raise Exception('error in type_check_stmt, unexpected ' + repr(s))
    
  def type_check_tail(self, s, env):
    match s:      
      case If(Compare(left, [cmp], [right]), [Goto(_)], [Goto(_)]):
        left_t = self.type_check_atm(left, env)
        right_t = self.type_check_atm(right, env)
        self.check_type_equal(left_t, right_t, s) # not quite strict enough
      case Goto(label):
        pass
      case Return(value):
        value_t = self.type_check_exp(value, env)
      case _:
        raise Exception('error in type_check_tail, unexpected' + repr(s))

  def type_check(self, p):
    match p:
      case CProgram(body):
          env = {}
          while True:
              old_env = copy.deepcopy(env)
              for (l, ss) in body.items():
                  self.type_check_stmts(ss[:-1], env)
              self.type_check_tail(ss[-1], env)
              if env == old_env:
                  break
          # because of explicate_control there can be undefined vars -Jeremy
          # undefs = [x for x,t in env.items() if t == Bottom()]
          # if undefs:
          #     raise Exception('error: undefined type for ' + str(undefs)) 
          p.var_types = env
      case _:
        raise Exception('error in type_check, unexpected ' + repr(p))
