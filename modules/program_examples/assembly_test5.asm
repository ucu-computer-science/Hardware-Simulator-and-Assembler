mov_low %R00, $1
mov_low %R01, $1
mov_low %R02, $20
cmp %R02, %R00
je $5
push %R00
add %R00, %R00, %R01
pop %R03
jmp $-5