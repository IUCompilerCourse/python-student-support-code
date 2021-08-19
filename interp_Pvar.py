from ast import *
from utils import input_int

class InterpPvar:
  def interp_exp(self, e, env):
    match e:
      case BinOp(left, Add(), right):
        l = self.interp_exp(left, env)
        r = self.interp_exp(right, env)
        return l + r
      case UnaryOp(USub(), v):
        return - self.interp_exp(v, env)
      case Name(id):
        return env[id]
      case Constant(value):
        return value
      case Call(Name('input_int'), []):
        return int(input())
      case _:
        raise Exception('error in InterpPvar.interp_exp, unhandled ' + repr(e))

  def interp_stmts(self, ss, env):
    if len(ss) == 0:
      return
    match ss[0]:
      case Assign([lhs], value):
        env[lhs.id] = self.interp_exp(value, env)
        return self.interp_stmts(ss[1:], env)
      case Expr(Call(Name('print'), [arg])):
        print(self.interp_exp(arg, env), end='')
        return self.interp_stmts(ss[1:], env)
      case Expr(value):
        self.interp_exp(value, env)
        return self.interp_stmts(ss[1:], env)
      case _:
        raise Exception('error in InterpPvar.interp_stmt, unhandled ' + repr(ss[0]))

  def interp_P(self, p):
    match p:
      case Module(body):
        self.interp_stmts(body, {})
    
if __name__ == "__main__":
  eight = Constant(8)
  neg_eight = UnaryOp(USub(), eight)
  read = Call(Name('input_int'), [])
  ast1_1 = BinOp(read, Add(), neg_eight)
  pr = Expr(Call(Name('print'), [ast1_1]))
  p = Module([pr])
  interp = InterpPvar()
  interp.interp_Pvar(p)
