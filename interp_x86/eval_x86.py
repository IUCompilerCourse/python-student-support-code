# Author: Joe Near
# License: GPLv3

from collections import defaultdict
from dataclasses import dataclass

from utils import *

from .convert_x86 import convert_program
from .parser_x86 import x86_parser, x86_parser_instrs


def interp_x86(program):
    x86_program = convert_program(program)
    emu = X86Emulator(logging=False)
    x86_output = emu.eval_program(x86_program)
    for s in x86_output:
        print(s, end='')

@dataclass
class FunPointer:
    fun_name: str

class X86Emulator:
    def __init__(self, logging=True):
        self.registers = defaultdict(lambda: None)
        self.memory = defaultdict(lambda: None)
        self.variables = defaultdict(lambda: None)
        self.logging = logging
        self.registers['rbp'] = 1000
        self.registers['rsp'] = 1000

        self.global_vals = {}

    def log(self, s):
        if self.logging:
            print(s)

    def parse_and_eval_program(self, s):
        p = x86_parser.parse(s)

    def eval_program(self, p):
        assert p.data == 'prog'
        blocks = {}
        output = []

        # transform the program into a dict of blocks
        for b in p.children:
            assert b.data == 'block'
            block_name, *instrs = b.children
            name = str(block_name)
            blocks[name] = instrs
            self.global_vals[name] = FunPointer(name)

        self.log('========== STARTING EXECUTION ==============================')

        # start evaluating at "main" or at "start"
        if label_name('main') in blocks.keys():
            self.eval_instrs(blocks[label_name('main')], blocks,
                             output)
        elif label_name('start') in blocks.keys():
            self.eval_instrs(blocks[label_name('start')], blocks,
                             output)


        self.log('FINAL STATE:')
        if self.logging:
            print(self.print_state())

        self.log(f'OUTPUT: {output}')
        self.log('========== FINISHED EXECUTION ==============================')

        return output

    def eval_instructions(self, s):
        import pandas as pd

        p = x86_parser_instrs.parse(s)

        assert p.data == 'instrs'
        blocks = {}
        output = []

        orig_memory = self.memory.copy()
        orig_registers = self.registers.copy()
        orig_variables = self.variables.copy()



        self.log('Executing instructions:')
        self.log(s)

        self.log('========== STARTING EXECUTION ==============================')

        # start evaluating at "main"
        self.eval_instrs(p.children, blocks, output)

        self.log('FINAL STATE:')
        if self.logging:
            print(self.print_state())

        self.log(f'OUTPUT: {output}')
        self.log('========== FINISHED EXECUTION ==============================')

        changes_memory = [[ f'mem {k}', orig_memory[k], self.memory[k] ] \
                          for k in self.diff_dicts(self.memory, orig_memory) ]
        changes_registers = [[ f'reg {k}',orig_registers[k],self.registers[k] ]\
                             for k in \
                             self.diff_dicts(self.registers, orig_registers) ]
        changes_variables =[[ f'var {k}',orig_variables[k],self.variables[k] ] \
                             for k in \
                             self.diff_dicts(self.variables, orig_variables) ]

        all_changes = changes_memory + changes_registers + changes_variables

        changes_df = pd.DataFrame(all_changes,
                                  columns=['Location', 'Old', 'New'])

        return changes_df

    def diff_dicts(self, d_after, d_orig):
        keys_diff = []
        for k in d_after.keys():
            if d_orig[k] != d_after[k]:
                keys_diff.append(k)
        return keys_diff

    def print_state(self):
        import pandas as pd

        pd.set_option("display.max_rows", None)
        memory = [[ f'mem {k}', self.memory[k] ] \
                  for k in sorted(self.memory.keys()) ]
        registers = [[ f'reg {k}', self.registers[k] ] \
                     for k in self.registers.keys() ]
        variables = [[ f'var {k}', self.variables[k] ] \
                     for k in self.variables.keys() ]
        gvals = [[ f'{k}', self.global_vals[k] ] \
                 for k in self.global_vals.keys() ]

        all_state = memory + registers + variables + gvals

        state_df = pd.DataFrame(all_state, columns=['Location', 'Value'])

        return state_df

    def print_mem(self, mem):
        for k, v in mem.items():
            self.log(f' {k}:\t {v}')

    def eval_imm(self, e) -> int:
        if e.data == 'int_a':
           v = int(e.children[0])
           if is_int64(v):
               return v
           else: 
               raise Exception('eval_imm: invalid immediate:', v)
             
        # if e.data == 'int_a':
        #     return int(e.children[0])
        # elif e.data == 'neg_a':
        #     return -self.eval_imm(e.children[0])
        else:
            raise Exception('eval_imm: unknown immediate:', e)


    def eval_arg(self, a):
        if a.data == 'reg_a':
            return self.registers[str(a.children[0])]
        elif a.data == 'var_a':
            return self.variables[str(a.children[0])]
        # elif a.data == 'int_a' or a.data == 'neg_a':
        #     return self.eval_imm(a)
        elif a.data == 'int_a':
            return self.eval_imm(a)
        elif a.data == 'neg_a':
            return neg64(self.eval_imm(a.children[0]))
        elif a.data == 'mem_a':
            offset, reg = a.children
            addr = self.registers[reg]
            offset_addr = add64(addr,self.eval_imm(offset))
            # offset_addr = addr + self.eval_imm(offset)
            return self.memory[offset_addr]
        elif a.data == 'global_val_a':
            loc, reg = a.children
            assert str(reg) == 'rip', a
            return self.global_vals[str(loc)]
        else:
            raise RuntimeError(f'Unknown arg in eval_arg: {a}')

    def store_arg(self, a, v):
        if a.data == 'reg_a':
            self.registers[str(a.children[0])] = v
        elif a.data == 'var_a':
            self.variables[str(a.children[0])] = v
        elif a.data == 'mem_a':
            offset, reg = a.children
            addr = self.registers[reg]
            #offset_addr = addr + self.eval_imm(offset)
            offset_addr = add64(addr,self.eval_imm(offset))
            self.memory[offset_addr] = v
        elif a.data == 'direct_mem_a':
            reg = a.children[0]
            addr = self.registers[reg]
            self.memory[addr] = v
        elif a.data == 'global_val_a':
            loc, reg = a.children
            assert str(reg) == 'rip', a
            self.global_vals[str(loc)] = v

        else:
            raise RuntimeError(f'Unknown arg in store_arg: {a}')

    def eval_instrs(self, instrs, blocks, output):
        for instr in instrs:
            self.log(f'Evaluating instruction: {instr.pretty()}')
            if instr.data == 'pushq':
                a = instr.children[0]
                self.registers['rsp'] = self.registers['rsp'] - 8
                v = self.eval_arg(a)
                self.memory[self.registers['rsp']] = v

            elif instr.data == 'popq':
                a = instr.children[0]
                v = self.memory[self.registers['rsp']]
                self.registers['rsp'] = self.registers['rsp'] + 8
                self.store_arg(a, v)

            elif instr.data == 'movq':
                a1, a2 = instr.children
                v = self.eval_arg(a1)
                self.store_arg(a2, v)

            elif instr.data == 'movzbq':
                a1, a2 = instr.children
                v = self.eval_arg(a1)
                self.store_arg(a2, v)

            elif instr.data == 'addq':
                a1, a2 = instr.children
                v1 = self.eval_arg(a1)
                v2 = self.eval_arg(a2)
                self.store_arg(a2, add64(v1, v2))

            elif instr.data == 'subq':
                a1, a2 = instr.children
                v1 = self.eval_arg(a1)
                v2 = self.eval_arg(a2)
                self.store_arg(a2, sub64(v2, v1))

            elif instr.data == 'xorq':
                a1, a2 = instr.children
                v1 = self.eval_arg(a1)
                v2 = self.eval_arg(a2)
                self.store_arg(a2, xor64(v1, v2))

            elif instr.data == 'negq':
                a1 = instr.children[0]
                v1 = self.eval_arg(a1)
                self.store_arg(a1, neg64(v1))

            elif instr.data in ['jmp', 'je', 'jne', 'jl', 'jle', 'jg', 'jge']:
                target = str(instr.children[0])
                perform_jump = False

                if instr.data == 'jmp':
                    perform_jump = True
                elif instr.data == 'je' and self.registers['EFLAGS'] == 'e':
                    perform_jump = True
                elif instr.data == 'jne' \
                     and self.registers['EFLAGS'] in ['g','l']:
                    perform_jump = True
                elif instr.data == 'jl' and self.registers['EFLAGS'] == 'l':
                    perform_jump = True
                elif instr.data == 'jle' \
                     and self.registers['EFLAGS'] in ['l', 'e']:
                    perform_jump = True
                elif instr.data == 'jg' and self.registers['EFLAGS'] == 'g':
                    perform_jump = True
                elif instr.data == 'jge' \
                     and self.registers['EFLAGS'] in ['g', 'e']:
                    perform_jump = True

                if perform_jump:
                    if target in blocks.keys():
                        self.eval_instrs(blocks[target], blocks, output)
                    elif target == label_name('conclusion'):
                        return
                    else:
                        raise Exception('jump to invalid target ' + target)
                    return # after jumping, toss continuation

            elif instr.data in ['sete', 'setne', 'setl', 'setle', 'setg', 'setge']:
                a1 = instr.children[0]

                if instr.data == 'sete' and self.registers['EFLAGS'] == 'e':
                    self.store_arg(a1, 1)
                elif instr.data == 'setne' and self.registers['EFLAGS'] != 'e':
                    self.store_arg(a1, 1)
                elif instr.data == 'setl' and self.registers['EFLAGS'] == 'l':
                    self.store_arg(a1, 1)
                elif instr.data == 'setle' \
                     and self.registers['EFLAGS'] in ['l', 'e']:
                    self.store_arg(a1, 1)
                elif instr.data == 'setg' and self.registers['EFLAGS'] == 'g':
                    self.store_arg(a1, 1)
                elif instr.data == 'setge' \
                     and self.registers['EFLAGS'] in ['g', 'e']:
                    self.store_arg(a1, 1)
                else:
                    self.store_arg(a1, 0)


            elif instr.data == 'callq':
                target = str(instr.children[0])
                if target == label_name('print_int'):
                    self.log(f'CALL TO print_int: {self.registers["rdi"]}')
                    output.append(self.registers['rdi'])
                    if self.logging:
                        print(self.print_state())

                elif target == label_name('read_int'):
                    self.registers['rax'] = input_int()
                    self.log(f'CALL TO read_int: {self.registers["rax"]}')
                    if self.logging:
                        print(self.print_state())

                elif target == 'initialize':
                    self.log(f'CALL TO initialize: {self.registers["rdi"]}, {self.registers["rsi"]}')
                    rootstack_size = self.registers['rdi']
                    heap_size = self.registers['rsi']

                    rs_begin = 2000
                    rs_end = rs_begin + rootstack_size

                    fromspace_begin = 100000
                    fromspace_end = fromspace_begin + heap_size

                    self.global_vals = { **self.global_vals,
                        'rootstack_begin': rs_begin,
                        'rootstack_end': rs_end,
                        'free_ptr': fromspace_begin,
                        'fromspace_begin': fromspace_begin,
                        'fromspace_end': fromspace_end
                    }

                    if self.logging:
                        print(self.print_state())


                elif target == 'collect':
                    self.log(f'CALL TO collect: need {self.registers["rsi"]} bytes')

                    needed = self.registers["rsi"]
                    fsb = self.global_vals['fromspace_begin']
                    fse = self.global_vals['fromspace_end']

                    current_space = fse - fsb

                    new_space = current_space
                    while new_space - current_space < needed:
                        new_space = new_space * 2

                    new_fse = fsb + new_space
                    self.global_vals['fromspace_end'] = new_fse

                    if self.logging:
                        print(self.print_state())

                else:
                    self.eval_instrs(blocks[target], blocks, output)

            elif instr.data == 'retq':
                return

            elif instr.data == 'cmpq':
                a1, a2 = instr.children
                v1 = self.eval_arg(a1)
                v2 = self.eval_arg(a2)

                if v1 == v2:
                    self.registers['EFLAGS'] = 'e'
                elif v2 < v1:
                    self.registers['EFLAGS'] = 'l'
                elif v2 > v1:
                    self.registers['EFLAGS'] = 'g'
                else:
                    raise RuntimeError(f'failed comparison: {instr}')

            elif instr.data == 'leaq':
                a1, a2 = instr.children
                v1 = self.eval_arg(a1)
                assert isinstance(v1, FunPointer)
                self.store_arg(a2, v1)

            elif instr.data == 'indirect_callq':
                v = self.eval_arg(instr.children[0])
                assert isinstance(v, FunPointer)
                target = v.fun_name
                self.eval_instrs(blocks[target], blocks, output)

            elif instr.data == 'indirect_jmp':
                v = self.eval_arg(instr.children[0])
                assert isinstance(v, FunPointer)
                target = v.fun_name
                self.eval_instrs(blocks[target], blocks, output)
                return # after jumping, toss continuation

            else:
                raise RuntimeError(f'Unknown instruction: {instr.data}')

            if self.logging:
                print(self.print_state())




prog1 = """
 .globl main
main:
 pushq %rbp
 movq %rsp, %rbp
 subq $16, %rsp
 jmp start
start:
 movq $42, -8(%rbp)
 movq -8(%rbp), %rax
 jmp conclusion
conclusion:
 movq %rax, %rdi
 callq print_int
 movq $0, %rax
 addq $16, %rsp
 popq %rbp
 retq
"""

prog2 = """
 .globl main
main:
 pushq %rbp
 movq %rsp, %rbp
 subq $16, %rsp
 jmp start
start:
 movq $38, -8(%rbp)
 addq $4, -8(%rbp)
 movq -8(%rbp), %rax
 jmp conclusion
conclusion:
 movq %rax, %rdi
 callq print_int
 movq $0, %rax
 addq $16, %rsp
 popq %rbp
 retq
"""

prog3 = """
 .globl main
main:
 pushq %rbp
 movq %rsp, %rbp
 subq $16, %rsp
 jmp start
start:
 movq $34, -8(%rbp)
 addq $3, -8(%rbp)
 movq -8(%rbp), %rax
 movq %rax, -16(%rbp)
 addq $5, -16(%rbp)
 movq -16(%rbp), %rax
 jmp conclusion
conclusion:
 movq %rax, %rdi
 callq print_int
 movq $0, %rax
 addq $16, %rsp
 popq %rbp
 retq
"""

prog4 = """
 .globl main
main:
 pushq %rbp
 movq %rsp, %rbp
 subq $16, %rsp
 jmp start
start:
 movq $5, -8(%rbp)
 movq -8(%rbp), %rax
 movq %rax, -16(%rbp)
 addq $37, -16(%rbp)
 movq -16(%rbp), %rax
 jmp conclusion
conclusion:
 movq %rax, %rdi
 callq print_int
 movq $0, %rax
 addq $16, %rsp
 popq %rbp
 retq
"""

prog5 = """
 .globl main
main:
 pushq %rbp
 movq %rsp, %rbp
 subq $32, %rsp
 jmp start
start:
 movq $5, -8(%rbp)
 addq $6, -8(%rbp)
 movq -8(%rbp), %rax
 movq %rax, -16(%rbp)
 addq $3, -16(%rbp)
 movq -8(%rbp), %rax
 movq %rax, -24(%rbp)
 movq -16(%rbp), %rax
 addq %rax, -24(%rbp)
 movq -24(%rbp), %rax
 movq %rax, -32(%rbp)
 addq $17, -32(%rbp)
 movq -32(%rbp), %rax
 jmp conclusion
conclusion:
 movq %rax, %rdi
 callq print_int
 movq $0, %rax
 addq $32, %rsp
 popq %rbp
 retq
"""

instrs = ['movq $1, %rax',
          'addq $2, %rax',
          'addq $3, %rax',
          'addq $5, %rax\n movq %rax, %rdi',
          'movq $42, (%rax)']

if __name__ == "__main__":
    for prog in prog1, prog2, prog3, prog4, prog5:
        emu = X86Emulator(logging=True)
        emu.eval_program(prog)

    emu = X86Emulator(logging=False)
    for i in instrs:
        print(emu.eval_instructions(i))
