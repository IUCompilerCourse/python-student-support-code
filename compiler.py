import ast
from ast import *
from utils import *
from x86_ast import *
import os
from typing import List, Tuple, Set, Dict

Binding = Tuple[Name, expr]
Temporaries = List[Binding]


class Compiler:

    ############################################################################
    # Remove Complex Operands
    ############################################################################

    def rco_exp(self, e: expr, need_atomic : bool) -> Tuple[expr, Temporaries]:
        match e:
          case  Constant(n):
            return Constant(n), []
          case Call(Name('input_int'),[]):
            if need_atomic:
              tmp = Name(generate_name('tmp'))
              return tmp, [(tmp, Call(Name('input_int'),[]))]
            else:
              return Call(Name('input_int'),[]), []
          case UnaryOp(USub(), exp):
             (atm, temps) = self.rco_exp(exp, True)
             usub = UnaryOp(USub(), atm)
             if need_atomic:
               tmp = Name(generate_name('tmp'))
               return tmp, temps + [(tmp, usub)]
             else:
               return usub, temps
          case BinOp(exp1, Add(), exp2):
             (atm1, temps1) = self.rco_exp(exp1, True)
             (atm2, temps2) = self.rco_exp(exp2, True)
             add = BinOp(atm1, Add(), atm2)
             if need_atomic:
               tmp = Name(generate_name('tmp'))
               return tmp, temps1 + temps2 + [(tmp, add)]
             else:
               return add, temps1 + temps2
          case BinOp(exp1, Sub(), exp2):
             (atm1, temps1) = self.rco_exp(exp1, True)
             (atm2, temps2) = self.rco_exp(exp2, True)
             sub = BinOp(atm1, Sub(), atm2)
             if need_atomic:
               tmp = Name(generate_name('tmp'))
               return tmp, temps1 + temps2 + [(tmp, sub)]
             else:
               return sub, temps1 + temps2
          case Name(var):
             return Name(var), []
          case _:
            raise Exception('rco_exp unexpected ' + repr(e))

    def rco_stmt(self, s: stmt) -> List[stmt]:
      match s:
        case Expr(Call(Name('print'), [exp])):
           (atm, temps) = self.rco_exp(exp, True)
           return [Assign([var], init) for (var,init) in temps] + [Expr(Call(Name('print'), [atm]))]
        case Expr(exp) :
           (atm, temps) = self.rco_exp(exp, False)
           return [Assign([var], init) for (var,init) in temps]
        case Assign([Name(var)], exp):
           (atm, temps) = self.rco_exp(exp, False)
           return [Assign([x], init) for (x,init) in temps] + [Assign([Name(var)], atm)]
        case _:
          raise Exception('rco_stmt not implemented')

    def remove_complex_operands(self, p: Module) -> Module:
        match p:
          case Module(ss):
            sss = [self.rco_stmt(s) for s in ss]
            return Module(sum(sss, []))
        raise Exception('remove_complex_operands not implemented')
        

    ############################################################################
    # Select Instructions
    ############################################################################

    def select_arg(self, e: expr) -> arg:
        # YOUR CODE HERE
        pass        

    def select_stmt(self, s: stmt) -> List[instr]:
        # YOUR CODE HERE
        pass        

    def select_instructions(self, p: Module) -> X86Program:
        # YOUR CODE HERE
        pass        

    ############################################################################
    # Assign Homes
    ############################################################################

    def assign_homes_arg(self, a: arg, home: Dict[Variable, arg]) -> arg:
        # YOUR CODE HERE
        pass        

    def assign_homes_instr(self, i: instr,
                           home: Dict[Variable, arg]) -> instr:
        # YOUR CODE HERE
        pass        

    def assign_homes(self, p: X86Program) -> X86Program:
        # YOUR CODE HERE
        pass        

    ############################################################################
    # Patch Instructions
    ############################################################################

    def patch_instr(self, i: instr) -> List[instr]:
        # YOUR CODE HERE
        pass        

    def patch_instructions(self, p: X86Program) -> X86Program:
        # YOUR CODE HERE
        pass        

    ############################################################################
    # Prelude & Conclusion
    ############################################################################

    def prelude_and_conclusion(self, p: X86Program) -> X86Program:
        # YOUR CODE HERE
        pass        

