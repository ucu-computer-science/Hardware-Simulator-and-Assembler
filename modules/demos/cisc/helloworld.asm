# Hello World PrintOut | Register-CISC example Assembly program

# The first option of the program is aimed to printout 'Hello World!',
# showing how CISC instructions might appear easier for user

# The second  option (which goes below the main one) is aimed not only to printout 'Hello World!',
# but also to show SIMD functionality of CISC architecture
# Letters are loaded into the memory and then printed out in the loop (in parts of three)

# First option
# Push letters (ASCII-codes) into the memory
push $33
push $100
push $108
push $114
push $111
push $119
push $32
push $111
push $108
push $108
push $101
push $72

# Set maximum counter value to 12
mov %R01, $12

# Main loop for printing out letters
.loop
pop %R03
out $1, %R03
# Increment counter and check condition
inc %R00
cmp %R00, %R01
jl .loop

# Finish the program
nop


# Second (SIMD) option
mov %R01, $33
mov %R02, $100
mov %R03, $108

store4 [%R00]
mov %R01, $8
add %R00, %R01

mov %R01, $114
mov %R02, $111
mov %R03, $119

store4 [%R00]
mov %R01, $8
add %R00, %R01

mov %R01, $32
mov %R02, $111
mov %R03, $108

store4 [%R00]
mov %R01, $8
add %R00, %R01

mov %R01, $108
mov %R02, $101
mov %R03, $72

store4 [%R00]

.mainloop
load4 [%R00]
out $1, %R03
out $1, %R02
out $1, %R01
cmp %R00, $0
je .end
mov %R01, $8
sub %R00, %R01
jmp .mainloop

.end
nop