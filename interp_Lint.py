from ast import *
from utils import input_int

def interp_exp(e):
    match e:
        case BinOp(left, Add(), right):
            l = interp_exp(left); r = interp_exp(right)
            return l + r
        case BinOp(left, Sub(), right):
            l = interp_exp(left); r = interp_exp(right)
            return l - r
        case UnaryOp(USub(), v):
            return - interp_exp(v)
        case Constant(value):
            return value
        case Call(Name('input_int'), []):
            return int(input())
        case _:
            raise Exception('error in interp_exp, unexpected ' + repr(e))

def interp_stmt(s):
    match s:
        case Expr(Call(Name('print'), [arg])):
            print(interp_exp(arg))
        case Expr(value):
            interp_exp(value)

def interp(p):
    match p:
        case Module(body):
            for s in body:
                interp_stmt(s)

# This version is for InterpLvar to inherit from 
class InterpLint:
  def interp_exp(self, e, env):
    match e:
      case BinOp(left, Add(), right):
        l = self.interp_exp(left, env); r = self.interp_exp(right, env)
        return l + r
      case BinOp(left, Sub(), right):
        l = self.interp_exp(left, env); r = self.interp_exp(right, env)
        return l - r
      case UnaryOp(USub(), v):
        return - self.interp_exp(v, env)
      case Constant(value):
        return value
      case Call(Name('input_int'), []):
        return int(input())
      case _:
        raise Exception('error in interp_exp, unexpected ' + repr(e))

  def interp_stmts(self, ss, env):
    if len(ss) == 0:
      return
    match ss[0]:
      case Expr(Call(Name('print'), [arg])):
        print(self.interp_exp(arg, env), end='')
        return self.interp_stmts(ss[1:], env)
      case Expr(value):
        self.interp_exp(value, env)
        return self.interp_stmts(ss[1:], env)
      case _:
        raise Exception('error in interp_stmts, unexpected ' + repr(ss[0]))

  def interp(self, p):
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
  interp_Lint(p)
