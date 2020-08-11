# There are 38 different instructions for RISC1 ISA (counting different operand types for the same instructions)
# This assembly program aims to meaningfully test all of them, with edge cases considered
#########################################################################################
mov $1022
mov $5
push
load
# Pushes 5 onto the stack, and then reads it from the stack to TOS
loadf
load $1022
mov $0
store $128
mov $128
storef
pushf
mov $12
mov $15
swap
dup2
dup
push
mov $1
pop
push
popf
# add
# sub
# mul
# div
# and
# or
# xor
# not
# lsh
# rsh
# call $
# call
# ret
# cmpe
# cmpe  $
# cmpb
# cmpb $
# test
# test $
# jmp
# jmp $
# jc
# jc $
# in $
# out $