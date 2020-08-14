# Hello World PrintOut | Accumulator-RISC example Assembly program
# Push the ASCII encodings onto the stack, and load the first letter into ACC register
mov $31
push
mov $33
push
mov $100
push
mov $108
push
mov $114
push
mov $111
push
mov $119
push
mov $32
push
mov $111
push
mov $108
push
mov $108
push
mov $101
push
mov $72

# Check if we have already finished printing the alphabet
cmp $31

# Jump to the end of the program if we are finished with printing
je $6

# Output a new letter to the device at port 1
out $1

# Pop the new letter into ACC register
pop

# Jump back to the start of the loop
jmp $-4