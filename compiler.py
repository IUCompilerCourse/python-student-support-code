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

    def rco_exp(self, e: expr) -> Tuple[expr, Temporaries]:
        match e:
          case  Constant(int):
            
          case Call(Name('input_int'),[]):
          
          case UnaryOp(USub(), exp):
             (new_exp, temps) = self.rco_exp(exp)
             
          case BinOp(exp1, Add(), exp2):
             (new_exp1, temps1) = self.rco_exp(exp1)
             (new_exp2, temps2) = self.rco_exp(exp2)
          
          case BinOp(exp1, Sub(), exp2):
             (new_exp1, temps1) = self.rco_exp(exp1)
             (new_exp2, temps2) = self.rco_exp(exp2)
          
          case Name(var):
          
          case _:
            raise Exception('rco_exp unexpected ' + repr(e))

    def rco_stmt(self, s: stmt) -> List[stmt]:
        # YOUR CODE HERE
        raise Exception('rco_stmt not implemented')

    def remove_complex_operands(self, p: Module) -> Module:
        # YOUR CODE HERE
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

