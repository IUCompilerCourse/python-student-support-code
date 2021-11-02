from utils import input_int

class InterpRVar:

    def interp_exp(env, e):
        match e:
            case Constant(n):
              return n
            case Call(Name('input_int'), []):
              return input_int()
            case UnaryOp(USub(), e1):
              return - interp_exp(e1)
            case BinOp(e1, Add(), e2):
              return interp_exp(e1) + interp_exp(e2)
            case _:
              return False

    def interp_Rint(p):
        match p:
            case Module(e):
              
