# There are 38 different instructions for Stack RISC1 ISA (counting different operand types for the same instructions)
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
mov $1
mov $2
add
mov $3
mov $2
sub
mov $3
mov $-1
mul
mov $2
mov $6
div
mov $6
mov $3
and
mov $6
mov $1
or
mov $6
mov $3
xor
mov $15
not
mov $2
lsh $1
rsh $1
call $2
add
call
call $2
ret
mov $2
mov $2
cmpe
mov $2
mov $3
cmpe
cmpe $0
cmpe $5
mov $2
mov $1
mov $2
cmpb
jc
nop
mov $0
jc $2
jmp $2
nop
mov $69
out $1
in $1