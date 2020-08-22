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
enter $5
leave
add %R00, [%R00]
add %R00, %R01
add %R01, [%R01+$2]
mov %R00, $512
add [%R00], %R00
mov %R01, $514
sub %R01, [%R01]
sub %R00, %R01
sub %R00, [%R00+$2]
mov %R00, $514
sub %R00, [%R00+$-2]
inc %R00
inc [%R01]
inc [%R01+$2]
dec %R00
dec [%R01]
dec [%R01+$2]
mov %R00, $2
mov %R01, $6
mov %R02, $514
mul %R00, %R01
div %R00, %R01
mul %R00, [%R02]
div %R00, [%R02]
mul [%R02], %R00
div [%R02], %R00
mul %R01, $3
div %R01, $3
mov %R02, $512
mul %R00, [%R02+$2]
div %R00, [%R02+$2]
and %R00, %R01
mov %R01, $5
or %R00, %R01
and %R00, [%R02]
or %R00, [%R02]
mov %R00, $5
mov %R01, $2
xor %R00, %R01
xor %R00, [%R02]
not %R00
not [%R02]
mov %R00, $4
lsh %R00, $1
rsh %R00, $1
rsh [%R02], $1
lsh [%R02], $1
rsh [%R02+$2], $1
lsh [%R02+$2], $1
call $2
nop
call %R00
call %R00+$1
jmp $5
nop
ret
nop
ret
nop
jmp %R00
nop
nop
nop
mov %R00, $-5
jmp %R00+$1
# Still have to test all of the compares, tests and almost all jumps :(((((
# Gonna have to implement SIMD too, have no idea howwwwwwwww

# cmp
# reg reg

# cmp
# reg imm

# cmp
# reg memreg

# cmp
# reg reg imm

# test
# reg reg

# test
# reg memreg

# test
# reg reg imm

# test
# memreg reg

# je
# imm

# jne
# imm

# jg
# imm

# jge
# imm

# jl
# imm

# jle
# imm

# in
# reg imm

# in
# mereg imm

# in
# reg imm imm

# out
# imm reg

# out
# imm memreg

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