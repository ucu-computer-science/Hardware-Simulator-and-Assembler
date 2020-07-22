mov_low %R00, $20
mov_low %R01, $1
mov_low %R02, $50
store [%R01], %R00
load %R02, [%R01]
mov %R00, %R02
mov_high %R02, $5
push %R02
pop %R03
add %R02, %R02, %R00
sub %R02, %R02, %R00
mul %R02, %R02, %R00
div %R02, %R02, %R00
and %R02, %R02, %R00
or %R02, %R02, %R00
xor %R02, %R02, %R00
not %R00, %R02
lsh %R02, %R02, %R00
rsh %R02, %R02, %R00
call %R00
ret
cmp %R02, %R02
cmp %R02, %R03
test %R02, %R03
jle $27
out $4, %R02
jmp $9