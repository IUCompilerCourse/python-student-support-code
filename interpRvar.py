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

  def interp_stmt(s):
    match s:
      case Call(Name('print'), [e]):
        print(interp_exp(e)) 
      case Expr(e):
        interp_exp(e) 
      case _:
        return 

  def interp_Rint(p):
    match p:
      case Module(body):
        for s in body:
            interp_stmt(s)

if __name__ == "__main__":
  eight = Constant(8)
  neg_eight = UnaryOp(USub(), eight)
  read = Call(Name('input_int'), [])
  ast1_1 = BinOp(read, Add(), neg_eight)
  pr = Call(Name('print'), [ast1_1])
  p = Module([pr])
  interp_Rint(p)
