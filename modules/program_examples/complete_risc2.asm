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
mov $3
call
nop
nop
call $2
jmp $2
ret
mov $3
jmp
nop
nop
mov $2
store $2
cmp
je $2
nop
cmp $3
je
cmp $3
jne
nop
jne $2
nop
test
test $0
in $1
mov $69
out $1