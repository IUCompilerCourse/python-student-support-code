from ast import *
from utils import input_int

def interp_exp(e):
    match e:
        case BinOp(left, Add(), right):
            l = interp_exp(left)
            r = interp_exp(right)
            return l + r
        case UnaryOp(USub(), v):
            return - interp_exp(v)
        case Constant(value):
            return value
        case Call(Name('input_int'), []):
            return int(input())            

def interp_stmt(s):
    match s:
        case Expr(Call(Name('print'), [arg])):
            print(interp_exp(arg))
        case Expr(value):
            interp_exp(value)

def interp_P(p):
    match p:
        case Module(body):
            for s in body:
                interp_stmt(s)
    
if __name__ == "__main__":
  eight = Constant(8)
  neg_eight = UnaryOp(USub(), eight)
  read = Call(Name('input_int'), [])
  ast1_1 = BinOp(read, Add(), neg_eight)
  pr = Expr(Call(Name('print'), [ast1_1]))
  p = Module([pr])
  interp_Pint(p)
