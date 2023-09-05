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
        if isinstance(e, bool):
            return e, []
        
        elif isinstance(e, int):
            return e, []
        
        elif isinstance(e, Name):
            if need_atomic:
                return e, []
            else:
                temp = Name(generate_name("temp"))
                return temp, [(temp, e)]
            
        elif isinstance(e, BinOp):
            lhs, lhs_temporaries = self.rco_exp(e.left, True)
            rhs, rhs_temporaries = self.rco_exp(e.right, True)

            temp = Name(generate_name("temp"))
            return temp, lhs_temporaries + rhs_temporaries + [(temp, BinOp(lhs, e.op, rhs))]
        
        elif isinstance(e, Let):
            var = e.var
            var_temporaries = self.rco_exp(e.rhs, False)
            body, body_temporaries = self.rco_exp(e.body, need_atomic)
            
            # Combine temporaries from the rhs and body.
            all_temporaries = var_temporaries + body_temporaries

            return body, all_temporaries
        raise Exception('rco_exp not implemented')

    def rco_stmt(self, s: stmt) -> List[stmt]:
        # YOUR CODE HERE
        if isinstance(s, Assign):
            target, target_temporaries = self.rco_exp(s.lhs, False)
            source, source_temporaries = self.rco_exp(s.rhs, True)

            #Combine temporaries from the lhs and rhs..
            all_temporaries = target_temporaries + source_temporaries

            return all_temporaries + [Assign(target, source)]
        
        elif isinstance(s, If):
            condition, condition_temporaries = self.rco_exp(s.cond, False)
            true_branch = self.rco_stmt(s.true)
            false_branch = self.rco_stmt(s.false)

            return(
                condition_temporaries + [If(condition, Seq(true_branch), Seq(false_branch))]
            )

        elif isinstance(s, Seq):
            stmts = []
            temporaries = []
            for sub_stmt in s.stmts:
                sub_stmt_temporaries = self.rco_stmt(sub_stmt)
                temporaries += sub_stmt_temporaries
                stmts.append(sub_stmt_temporaries[-1])  # Append the last statement.   

            return temporaries + [Seq(stmts)]
        raise Exception('rco_stmt not implemented')

    def remove_complex_operands(self, p: Module) -> Module:
        # YOUR CODE HERE
        transformed_statements = []
        for stmt in p.body:
            rco_statements = self.rco_stmt(stmt)
            transformed_statements.extend(rco_statements)

        #Create a new Module with the transformed statements.
        transformed_program = Module(transformed_statements)
        
        return transformed_program
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
        # We define every arg, but what does 'home' do?
        # I think currently, arg is actually a Variable.
        # We actually build a reverse-dict?
        # Varibale only have id, where to save offset?
        if a not in home.items():
            home[] = a
        pass        

    def assign_homes_instr(self, i: instr,
                           home: Dict[Variable, arg]) -> instr:
        # YOUR CODE HERE
        new_a = []
        for a in i.args:
            new_a.append(self.assign_homes_arg(a), home)
        return Instr(i.instr, new_a)

    def assign_homes_instrs(self, ss: List[instr],
                            home: Dict[Variable, arg]) -> List[instr]:
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
        res = []
        # if ("(" in str(i.source())) and ("(" in str(i.target())):
        if isinstance(i.source(), Deref) and isinstance(i.target(), Deref):
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
                for arg in instr.args:
                    if isinstance(arg, Deref):
                        max_offset = max(max_offset, arg.offset)
            prelude = [
                Instr("pushq", [Reg("rbp")]),
                Instr("movq", [Reg("rsp"), Reg("rbp")]),
                Instr("subq", [Immediate(max_offset), Reg("rsp")])
            ]
            
            conclusion = [
                Instr("addq", Immediate(max_offset), Reg("rsp")),
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