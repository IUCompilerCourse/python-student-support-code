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

  # The cont parameter is a list of statements that are the
  # continuaton of the current statement s.
  # We use this continuation-passing approach because
  # it enables the handling of Goto in interp_Cif.py.
  def interp_stmt(self, s, env, cont):
    match s:
      case Expr(Call(Name('print'), [arg])):
        val = self.interp_exp(arg, env)
        print(val, end='')
        return self.interp_stmts(cont, env)
      case Expr(value):
        self.interp_exp(value, env)
        return self.interp_stmts(cont, env)
      case _:
        raise Exception('error in interp_stmt, unexpected ' + repr(s))
    
  def interp_stmts(self, ss, env):
    if len(ss) == 0:
      return None
    else:
      return self.interp_stmt(ss[0], env, ss[1:])

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
  interp(p)
