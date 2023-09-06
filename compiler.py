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
        if isinstance(e, Constant):
            return e, []
        elif isinstance(e, Name):
            if not need_atomic:
                return e, []
            else:
                temp = Name(generate_name("temp"))
                return temp, [Assign([temp], e)]     
        elif isinstance(e, BinOp):
            lhs, lhs_temporaries = self.rco_exp(e.left, True)
            rhs, rhs_temporaries = self.rco_exp(e.right, True)
            temp = Name(generate_name("temp"))
            return temp, lhs_temporaries + rhs_temporaries + [Assign([temp], BinOp(lhs, e.op, rhs))]
        elif isinstance(e, UnaryOp):
            operand, operand_temporaries = self.rco_exp(e.operand, True)
            temp = Name(generate_name("temp"))
            return temp, operand_temporaries + [Assign([temp], UnaryOp(e.op, operand))]
        elif isinstance(e, Call):
            f_exp = []
            f_temporaries = []
            for a in e.args:
                t_exp, t_temp = self.rco_exp(a, True)
                f_exp.append(t_exp)
                f_temporaries += t_temp
            if isinstance(e.func, Name) and e.func.id == "print":
                return Call(e.func, f_exp), f_temporaries
            elif isinstance(e.func, Name) and e.func.id == "input_int":
                temp = Name(generate_name("temp"))
                return temp, [Assign([temp], Call(e.func, []))]
            else:
                temp = Name(generate_name("temp"))
                return temp, f_temporaries + [Assign([temp], Call(e.func, f_exp))]
        raise Exception('rco_exp not implemented')

    def rco_stmt(self, s: stmt) -> List[stmt]:
        if isinstance(s, Assign):
            # Since the target is typically a simple variable, it doesn't need RCO.
            # Just ensure it's in the proper format (a list with a single Name).
            target = s.targets[0]
            # Apply RCO to the source of the assignment.
            source, source_temporaries = self.rco_exp(s.value, True)

            return source_temporaries + [Assign([target], source)]
        
        elif isinstance(s, Expr):
            expr, temporaries = self.rco_exp(s.value, True)
            return temporaries + [Expr(expr)]
    

    def remove_complex_operands(self, p: Module) -> Module:
        transformed_statements = []
        for stmt in p.body:
            rco_statements = self.rco_stmt(stmt)
            transformed_statements += rco_statements
        #Create a new Module with the transformed statements.
        transformed_program = Module(transformed_statements)
        return transformed_program
        

    ############################################################################
    # Select Instructions
    ############################################################################

    def select_arg(self, e: expr) -> arg:
    # Implement the logic to select an argument for the target architecture.
        if isinstance(e, Name):
            return Variable(e.id)
        elif isinstance(e, Constant):
            return Immediate(e.value)
        # Errors for unhandled cases:
        else:
            raise Exception('select_arg not implemented')
        

    def select_stmt(self, s: stmt) -> List[instr]:
        if isinstance(s, Assign):
            target = self.select_arg(s.targets[0])
            if isinstance(s.value, BinOp):
                lhs = self.select_arg(s.value.left)
                rhs = self.select_arg(s.value.right)
                op = s.value.op
                if isinstance(op, Add):
                    return [Instr("movq", [lhs, target]), 
                            Instr("addq", [rhs, target])]
                elif isinstance(op, Sub):
                    return [Instr("movq", [lhs, target]), 
                            Instr("subq", [rhs, target])]
            elif isinstance(s.value, UnaryOp):
                target = self.select_arg(s.targets[0])
                op = s.value.op
                if isinstance(op, USub):  # assuming UMinus is the unary minus operation
                    return [Instr("negq", [target])]            
            elif isinstance(s.value, Call):
                if s.value.func.id == "input_int":
                    return [Callq(label_name("read_int"), 1),
                            Instr("movq", [Reg("rax"), self.select_arg(s.targets[0])])]
            source = self.select_arg(s.value)
            return [Instr("movq", [source, target])]
        # Handling Call instruction, e.g., print and input_int
        elif isinstance(s.value, Call):
            sv = s.value
            if isinstance(sv.func, Name):
                if sv.func.id == "print":
                    arg = self.select_arg(sv.args[0])
                    return [Instr("movq", [arg, Reg("rdi")]),
                            Callq(label_name("print_int"), 1)]
                elif sv.func.id == "input_int":
                    return [Callq(label_name("read_int"), 1),
                            Instr("movq", [Reg("rax"), self.select_arg(s.targets[0])])]
        else:
            raise Exception('select_stmt not implemented')


    def select_instructions(self, p: Module) -> X86Program:
        # Implement the logic to select instructions for a program
        selected_instructions = []
        for stmt in p.body:
            selected_stmt = self.select_stmt(stmt)
            selected_instructions += selected_stmt
        # Create a new X86Program with the selected instructions.
        x86_program = X86Program(selected_instructions)
        return x86_program       

    ############################################################################
    # Assign Homes
    ############################################################################

    def assign_homes_arg(self, a: arg, home: Dict[Variable, arg]) -> arg:
        # YOUR CODE HERE
        # We define every arg, but what does 'home' do?
        # I think currently, arg could be a Variable or other arg.
        if isinstance(a, Variable):
            return home[a]
        return a

    def assign_homes_instr(self, i: instr,
                           home: Dict[Variable, arg]) -> instr:
        # YOUR CODE HERE
        # create a new Instr
        new_a = []
        if isinstance(i, Instr):
            for a in i.args:
                new_a.append(self.assign_homes_arg(a, home))
            return Instr(i.instr, new_a)
        else:
            return i

    def assign_homes_instrs(self, ss: List[instr],
                            home: Dict[Variable, arg]) -> List[instr]:
        # YOUR CODE HERE
        new_instrs = []
        num_varibale = 0
        # first iteration, build a dict to save all variable and corresponding deref as key-value pairs
        for s in ss:
            if isinstance(s, Instr):
                for a in s.args:
                    if isinstance(a, Variable) and a not in home:
                        num_varibale += 1
                        home[a] = Deref("rbp", -8 * num_varibale)
        # second iteration, replace all variable
        for s in ss:
            new_instrs.append(self.assign_homes_instr(s, home))
        return new_instrs

    def assign_homes(self, p: X86Program) -> X86Program:
        # YOUR CODE HERE
        if isinstance(p.body, dict):
            assign_home_instrs = {}
            for label, instrs in p.body.items():
                assign_home_instrs[label] = self.assign_homes_instrs(instrs)
        else:
            home = {}
            assign_home_instrs = self.assign_homes_instrs(p.body, home)
        return X86Program(assign_home_instrs)

    ############################################################################
    # Patch Instructions
    ############################################################################

    def patch_instr(self, i: instr) -> List[instr]:
        # YOUR CODE HERE
        res = []
        # if ("(" in str(i.source())) and ("(" in str(i.target())):
        if isinstance(i, Instr) and isinstance(i.source(), Deref) and isinstance(i.target(), Deref):
            # two memory access, do patch instration operation
            # build two instration and add into list
            # I assume %rax as a intermediate register and always available
            # but how to check if it is in use?
            mov_instr = Instr("movq", [i.source(), Reg("rax")])
            # for movq, addq, subq, second operation should be same as original operation
            op_instr = Instr(i.instr, [Reg("rax"), i.target()])
            res.append(mov_instr)
            res.append(op_instr)
        else:
            # add instration into list
            res.append(i)
        return res

    def patch_instrs(self, ss: List[instr]) -> List[instr]:
        # YOUR CODE HERE
        res = []
        for s in ss:
            instr_res = self.patch_instr(s)
            for ins in instr_res:
                res.append(ins)
        return res

    def patch_instructions(self, p: X86Program) -> X86Program:
        # YOUR CODE HERE
        if isinstance(p.body, dict):
            patched_instrs = {}
            for label, instrs in p.body.items():
                patched_instrs[label] = self.patch_instrs(instrs)
        else:
            patched_instrs = self.patch_instrs(p.body)
        
        return X86Program(patched_instrs)

    ############################################################################
    # Prelude & Conclusion
    ############################################################################

    def prelude_and_conclusion(self, p: X86Program) -> X86Program:
        # YOUR CODE HERE
        # The problem is that how to know the size I need to allocate.
        # iterate on this program and 
        max_offset = 0 
        # If we have multiple functions (with labels)
        if isinstance(p.body, dict):
            for label, instrs in p.body.items():
                for instr in instrs:
                    if isinstance(instr, Instr):
                        for arg in instr.args:
                            if isinstance(arg, Deref):
                                max_offset = max(max_offset, arg.offset)
            new_body = {}
            for label, instrs in p.body.items():
                # instructions for stack allocations
                prelude = [
                    Instr("pushq", [Reg("rbp")]),
                    Instr("movq", [Reg("rsp"), Reg("rbp")]),
                    Instr("subq", [Immediate(max_offset), Reg("rsp")])
                ]
                # instructions for restore stack allocations
                conclusion = [
                    Instr("addq", Immediate(max_offset), Reg("rsp")),
                    # Instr("mov", ["%rbp", "%rsp"]), # is equal to addq if %rbp 's value is not changed
                    Instr("popq", [Reg("rbp")]),
                    Instr("retq", [])
                ]
                
                new_body[label] = prelude + instrs + conclusion          
        else:  
            # If we have a single main function
            for instr in p.body:
                if isinstance(instr, Instr):
                    for arg in instr.args:
                        if isinstance(arg, Deref):
                            max_offset = max(max_offset, arg.offset)
            prelude = [
                Instr("pushq", [Reg("rbp")]),
                Instr("movq", [Reg("rsp"), Reg("rbp")]),
                Instr("subq", [Immediate(max_offset), Reg("rsp")])
            ]
            
            conclusion = [
                Instr("addq", [Immediate(max_offset), Reg("rsp")]),
                Instr("popq", [Reg("rbp")]),
                Instr("retq", [])
            ]
            
            new_body = prelude + p.body + conclusion

        return X86Program(new_body)

    # challenge, exercise 2.7
    '''
    def pe_exp(e):
        match e:
            case BinOp(left, Add(), right):
                return pe_add(pe_exp(left), pe_exp(right))
            case BinOp(left, Sub(), right):
                return pe_sub(pe_exp(left), pe_exp(right))
            case UnaryOp(USub(), v):
                return pe_neg(pe_exp(v))
            case Constant(value):
                return e
            case Call(Name('input_int'), []):
                return e
    def pe_stmt(s):
        match s:
            case Expr(Call(Name('print'), [arg])):
                return Expr(Call(Name('print'), [pe_exp(arg)]))
            case Expr(value):
                return Expr(pe_exp(value))
    '''