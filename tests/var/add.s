	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $0, %rsp
    movq $40, -8(%rbp)
    addq $2, -8(%rbp)
    movq -8(%rbp), %rdi
    callq print_int
    addq $0, %rsp
    popq %rbp
    retq 

