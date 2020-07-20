mov_low %R00, $1
mov_low %R01, $1
mov_low %R02, $32
cmp %R02, %R00
je $4
push %R00
add %R00, %R00, %R01
jmp $-4