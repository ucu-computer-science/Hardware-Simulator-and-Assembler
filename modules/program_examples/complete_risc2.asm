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
mov $512
storei
add
sub
store
mov $2
mul
div
mov $3
store
mov $5
and
mov $5
or
mov $5
xor
not
rsh $1
lsh $1
nop
nop
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