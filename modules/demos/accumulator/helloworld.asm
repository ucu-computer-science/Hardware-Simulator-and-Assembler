# Hello World PrintOut | Accumulator example Assembly program

# Push the ASCII encodings onto the stack, and load the first letter into ACC register
# Directive .end contains last element 'Hello World!'

.end db 31

mov .end
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

.loop
# Check if we have already finished printing the alphabet
cmp .end

# Jump to the end of the program if we are finished with printing
je .finish

# Output a new letter to the device at port 1
out $1

# Pop the new letter into ACC register
pop

# Jump back to the start of the loop
jmp .loop

.finish
# Finish the program
nop