# There are 89 (I think?) different instructions for CISC ISA
# (counting different operand types for the same instructions)
# This assembly program aims to meaningfully test all of them, with edge cases considered
#########################################################################################
mov %R00, $512
mov %R01, %R00
mov %R00, [%R01]
mov %R00, [%R01+$2]
mov [%R01], %R00
mov [%R01], $666
mov %R01, $128
mov [%R01+$2], %R01
mov [%R01+$2], $512
push %R01
push $512
pop %R01

# enter
# enter
# imm

# leave
# leave


# add
# firstop
# reg memreg

# add
# firstop
# reg reg

# add
# firstop
# reg reg imm

# add
# firstop
# memreg reg

# sub
# firstop
# reg memreg

# sub
# firstop
# reg reg

# sub
# firstop
# reg reg imm

# sub
# firstop
# memreg reg

# inc
# firstop
# reg

# inc
# firstop
# memreg

# inc
# firstop
# reg off

# dec
# firstop
# reg

# dec
# firstop
# memreg

# dec
# firstop
# reg off

# mul
# firstop
# reg reg

# mul
# firstop
# reg memreg

# mul
# firstop
# memreg reg

# mul
# firstop
# reg imm

# mul
# firstop
# reg reg imm

# div
# firstop
# reg reg

# div
# firstop
# reg memreg

# div
# firstop
# memreg reg

# div
# firstop
# reg imm

# div
# firstop
# reg reg imm

# and
# firstop
# reg reg

# and
# firstop
# reg memreg

# or
# firstop
# reg reg

# or
# firstop
# reg memreg

# xor
# firstop
# reg reg

# xor
# firstop
# reg memreg

# not
# firstop
# reg

# not
# firstop
# memreg

# lsh
# firstop
# reg imm

# lsh
# firstop
# memreg imm

# lsh
# firstop
# reg imm imm

# rsh
# firstop
# reg imm

# rsh
# firstop
# memreg imm

# rsh
# firstop
# reg imm imm

# call
# call
# imm

# call
# call
# reg

# call
# call
# reg imm

# ret
# ret


# cmp
# flags
# reg reg

# cmp
# flags
# reg imm

# cmp
# flags
# reg memreg

# cmp
# flags
# reg reg imm

# test
# flags
# reg reg

# test
# flags
# reg memreg

# test
# flags
# reg reg imm

# test
# flags
# memreg reg

# jmp
# jmp
# imm

# jmp
# jmp
# reg

# jmp
# jmp
# reg imm

# je
# jmp
# imm

# jne
# jmp
# imm

# jg
# jmp
# imm

# jge
# jmp
# imm

# jl
# jmp
# imm

# jle
# jmp
# imm

# in
# in
# reg imm

# in
# in
# mereg imm

# in
# in
# reg imm imm

# out
# out
# imm reg

# out
# out
# imm memreg

# out
# out
# imm reg imm

# load4
# firstop
# memreg

# store4
# firstop
# memreg

# add4
# firstop
# memreg memreg

# sub4
# firstop
# memreg memreg

# mul4
# firstop
# memreg memreg

# div4
# firstop
# memreg memreg

# cmp4
# firstop
# memreg memreg

# test4
# firstop
# memreg memreg

# nop
# nop

