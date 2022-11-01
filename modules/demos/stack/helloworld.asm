# Hello World PrintOut | Stack example Assembly program

# These next instructions load ASCII encodings of characters in "Hello world!" into the register stack
# backwards, so that when the values are popped from the stack, we can output the values in a normal way
# Directive .end contains last element 'Hello World!'

.end db 31

mov .end
mov $33
mov $100
mov $108
mov $114
mov $111
mov $119
mov $32
mov $111
mov $108
mov $108
mov $101
mov $72

.loop
# Duplicate the value for the comparison
dup

# Check if we have already finished printing the alphabet
cmpe .end

# Jump to the end of the program if we are finished with printing
jc .finish

# Output TOS value to the device at port 1
out $1

# Jump back to the start of the loop
jmp .loop

.finish
# Finish the program
nop