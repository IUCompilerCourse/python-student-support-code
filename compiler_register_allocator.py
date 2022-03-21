import compiler
from graph import UndirectedAdjList
from typing import List, Tuple, Set, Dict
from ast import *
from x86_ast import *
from typing import Set, Dict, Tuple

# Skeleton code for the chapter on Register Allocation

class Compiler(compiler.Compiler):

    ###########################################################################
    # Uncover Live
    ###########################################################################

    def read_vars(self, i: instr) -> Set[location]:
        # YOUR CODE HERE
        pass

    def write_vars(self, i: instr) -> Set[location]:
        # YOUR CODE HERE
        pass

    def uncover_live(self, p: X86Program) -> Dict[instr, Set[location]]:
        # YOUR CODE HERE
        pass

    ############################################################################
    # Build Interference
    ############################################################################

    def build_interference(self, p: X86Program,
                           live_after: Dict[instr, Set[location]]) -> UndirectedAdjList:
        # YOUR CODE HERE
        pass

    ############################################################################
    # Allocate Registers
    ############################################################################

    # Returns the coloring and the set of spilled variables.
    def color_graph(self, graph: UndirectedAdjList,
                    variables: Set[location]) -> Tuple[Dict[location, int], Set[location]]:
        # YOUR CODE HERE
        pass

    def allocate_registers(self, p: X86Program,
                           graph: UndirectedAdjList) -> X86Program:
        # YOUR CODE HERE
        pass

    ############################################################################
    # Assign Homes
    ############################################################################

    def assign_homes(self, pseudo_x86: X86Program) -> X86Program:
        # YOUR CODE HERE
        pass

    ###########################################################################
    # Patch Instructions
    ###########################################################################

    def patch_instructions(self, p: X86Program) -> X86Program:
        # YOUR CODE HERE
        pass

    ###########################################################################
    # Prelude & Conclusion
    ###########################################################################

    def prelude_and_conclusion(self, p: X86Program) -> X86Program:
        # YOUR CODE HERE
        pass
