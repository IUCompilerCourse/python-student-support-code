# Author: Joe Near
# License: GPLv3

from lark import Lark

x86_parser = Lark(r"""
    ?instr: "movq" arg "," arg -> movq
          | "addq" arg "," arg -> addq
          | "subq" arg "," arg -> subq
          | "cmpq" arg "," arg -> cmpq
          | "xorq" arg "," arg -> xorq
          | "leaq" arg "," arg -> leaq
          | "negq" arg -> negq
          | "jmp" CNAME -> jmp
          | "jmp" "*" arg -> indirect_jmp
          | "je" CNAME -> je
          | "jl" CNAME -> jl
          | "jle" CNAME -> jle
          | "jg" CNAME -> jg
          | "jge" CNAME -> jge
          | "sete" arg -> sete
          | "setl" arg -> setl
          | "setle" arg -> setle
          | "setg" arg -> setg
          | "setge" arg -> setge
          | "movzbq" arg "," arg -> movzbq
          | "xorq" arg "," arg -> xorq
          | "andq" arg "," arg -> andq
          | "salq" arg "," arg -> salq
          | "sarq" arg "," arg -> sarq
          | "callq" CNAME -> callq
          | "callq" "*" arg -> indirect_callq
          | "pushq" arg -> pushq
          | "popq" arg -> popq
          | "retq" -> retq

    block: ".globl" CNAME
         |  ".align" NUMBER
         | CNAME ":" (instr)*

    ?arg: "$" atom -> int_a
        | "%" reg -> reg_a
        | "#" CNAME -> var_a
        | "(" "%" reg ")" -> direct_mem_a
        | atom "(" "%" reg ")" -> mem_a
        | CNAME "(" "%" reg ")" -> global_val_a

    ?atom: NUMBER -> int_a
         | "-" atom  -> neg_a

    !?reg: "rsp" | "rbp" | "rax" | "rbx" | "rcx" | "rdx" | "rsi" | "rdi" 
         | "r8" | "r9" | "r10" | "r11" | "r12" | "r13" | "r14" | "r15"
         | "al" | "rip"

    prog: block*

    %import common.NUMBER
    %import common.CNAME

    %import common.WS
    %ignore WS
    """, start='prog', parser='lalr')

x86_parser_instrs = Lark(r"""
    ?instr: "movq" arg "," arg -> movq
          | "addq" arg "," arg -> addq
          | "subq" arg "," arg -> subq
          | "cmpq" arg "," arg -> cmpq
          | "xorq" arg "," arg -> xorq
          | "leaq" arg "," arg -> leaq
          | "negq" arg -> negq
          | "jmp" CNAME -> jmp
          | "jmp" "*" arg -> indirect_jmp
          | "je" CNAME -> je
          | "jl" CNAME -> jl
          | "jle" CNAME -> jle
          | "jg" CNAME -> jg
          | "jge" CNAME -> jge
          | "sete" arg -> sete
          | "setl" arg -> setl
          | "setle" arg -> setle
          | "setg" arg -> setg
          | "setge" arg -> setge
          | "movzbq" arg "," arg -> movzbq
          | "xorq" arg "," arg -> xorq
          | "callq" CNAME -> callq
          | "andq" arg "," arg -> andq
          | "salq" arg "," arg -> salq
          | "sarq" arg "," arg -> sarq
          | "callq" "*" arg -> indirect_callq
          | "pushq" arg -> pushq
          | "popq" arg -> popq
          | "retq" -> retq

    instrs: instr*

    ?arg: "$" atom -> int_a
        | "%" reg -> reg_a
        | "#" CNAME -> var_a
        | "(" "%" reg ")" -> direct_mem_a
        | atom "(" "%" reg ")" -> mem_a
        | CNAME "(" "%" reg ")" -> global_val_a

    ?atom: NUMBER -> int_a
         | "-" atom  -> neg_a

    !?reg: "rsp" | "rbp" | "rax" | "rbx" | "rcx" | "rdx" | "rsi" | "rdi" 
         | "r8" | "r9" | "r10" | "r11" | "r12" | "r13" | "r14" | "r15"
         | "al" | "rip"

    %import common.NUMBER
    %import common.CNAME

    %import common.WS
    %ignore WS
    """, start='instrs', parser='lalr')

