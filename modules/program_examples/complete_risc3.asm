# There are 41 different instructions for RISC3 ISA (counting different operand types for the same instructions)
# Of those, only one is still not implemented completely ('in' instruction)
# This assembly program aims to meaningfully test all of them, with edge cases considered
#########################################################################################
# Checking the basic move instructions (mov_low should erase the high byte)
mov_high %R00, $2
mov_low %R00, $-1
# R00 contains the 0x00FF value

mov_high %R00, $2
mov %R01, %R00
# R00 and R01 contain the 0x0205 value

mov_low %R01, $0
mov_high %R01, $2
# R01 is now 0x0200 (the starting point of the program in memory)

load %R00, [%R01]
# R00 is now 0x2002

mov_low %R01, $0
store [%R01], %R00
# R01 now points at 0x0000 in memory, and 0x2002 is stored there

push %R00
pop %R01
# 0x2002 is pushed on to the stack, and popped into R01

add %R00, %R00, %R01
# 0x4004 is now in R00

sub %R00, %R00, %R01
# 0x2002 is now in R00

mov_low %R02, $2
mul %R01, %R01, %R02
# 0x4004 is now in R01

div %R01, %R01, %R02
# 0x2002 is now in R01

mov_low %R02, $5
and %R00, %R01, %R02
# R00 contains 0x0000

or %R00, %R01, %R02
# R00 contains 0x2007

xor %R00, %R00, %R01
# R00 contains 0x0005

not %R00, %R00
# R00 contains 0xFFFA

mov_low %R00, $5
mov_low %R02, $1
rsh %R00, %R00, %R02
# R00 contains 2

lsh %R00, %R00, %R02
# R00 contains 4

call $5
# Should transfer control straight to the call $-3
nop
call %R00
# Should go to ret
nop
jmp $3
call $-3
# Should transfer to call %R00
ret
# Should go to nop after call %R00
nop