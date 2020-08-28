.word dw "anime\0x061"
mov %R00, .word
out $1, %R00
mov %R00, .word+$1
out $1, %R00
mov %R00, .word+$2
out $1, %R00
mov %R00, .word+$3
out $1, %R00
mov %R00, .word+$4
out $1, %R00
mov %R00, .word+$5
out $1, %R00

# Offsets
.value db 7
.off1 db "example"
.off2 db 5
mov %R00, .value
mov %R01, $2
mov [%R01+.off1], %R00
mov [%R01+.off2], %R00