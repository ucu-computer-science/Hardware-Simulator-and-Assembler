# Hello World PrintOut | Register-CISC example Assembly program

# That option is aimed not only to printout 'Hello World!',
# but also to show SIMD functionality of CISC architecture
# Letters are loaded into the memory and then printed out in the loop (in parts of three)
# Directive .step contains length of the used vector (8 bytes)

.step db 8

# Store all the letters ib the memory (from finish to start)
mov %R01, $33
mov %R02, $100
mov %R03, $108

store4 [%R00]
mov %R01, .step
add %R00, %R01

mov %R01, $114
mov %R02, $111
mov %R03, $119

store4 [%R00]
mov %R01, .step
add %R00, %R01

mov %R01, $32
mov %R02, $111
mov %R03, $108

store4 [%R00]
mov %R01, .step
add %R00, %R01

mov %R01, $108
mov %R02, $101
mov %R03, $72

store4 [%R00]

# Printout letters by going through memory
.mainloop
load4 [%R00]
out $1, %R03
out $1, %R02
out $1, %R01
cmp %R00, $0
je .end

mov %R01, .step
sub %R00, %R01
jmp .mainloop

# Finish the program
.end
nop