	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    callq read_int
    movq %rax, -8(%rbp)
    movq -8(%rbp), %rax
    movq %rax, -16(%rbp)
    addq $0, %rsp
    popq %rbp
    retq 

