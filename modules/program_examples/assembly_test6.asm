mov_low %R00, $65
mov_low %R01, $1
mov_low %R02, $91
cmp %R02, %R00
je $4
out $1, %R00
add %R00, %R00, %R01
jmp $-4