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

    def rco_exp(self, e: expr, need_atomic: bool) -> Tuple[expr, Temporaries]:
        # YOUR CODE HERE
        pass

    def rco_stmt(self, s: stmt) -> List[stmt]:
        # YOUR CODE HERE
        pass
        

    def remove_complex_operands(self, p: Module) -> Module:
        # YOUR CODE HERE
        pass
        

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
                           home: Dict[location, arg]) -> instr:
        # YOUR CODE HERE
        pass        

    def assign_homes_instrs(self, ss: List[instr],
                            home: Dict[location, arg]) -> List[instr]:
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

    def patch_instrs(self, ss: List[instr]) -> List[instr]:
        # YOUR CODE HERE
        pass        

    def patch_instructions(self, p: X86Program) -> X86Program:
        # YOUR CODE HERE
        pass        

    ############################################################################
    # Generate Main Function
    ############################################################################

    def generate_main(self, p: X86Program) -> X86Program:
        # YOUR CODE HERE
        pass        

    ############################################################################
    # Print x86
    ############################################################################

    def print_x86(self, p: X86Program) -> str:
        # YOUR CODE HERE
        pass        

    def print_instr(self, i: instr) -> str:
        # YOUR CODE HERE
        pass        

    def print_arg(self, a: arg) -> str:
        # YOUR CODE HERE
        pass        
