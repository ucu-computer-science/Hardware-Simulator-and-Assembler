# There are 48 different instructions for RISC1 ISA (counting different operand types for the same instructions)
# This assembly program aims to meaningfully test all of them, with edge cases considered
#########################################################################################
mov $512
storei
load
inc
dec
loadf
loadi
store
store $228
storef
mov $277
push
pushf
pushi
popf
pop
popi
# add
# sub
# inc
# dec
# mul
# div
# and
# or
# xor
# not
# lsh
# rsh
# call
# call $
# ret
# cmp
# cmp $
# test
# test $
# jmp
# jmp $
# je
# je $
# jne
# jne $
# jg
# jg $
# jge
# jge $
# jl
# jl $
# jle
# jle $
# in $
# out $