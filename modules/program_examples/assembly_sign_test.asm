mov %R00, $512
mov %R01, %R00
mov [%R01+$2], %R00
mov [%R01-$2], %R00
jmp %R00-$513