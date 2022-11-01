# Alphabet PrintOut | Stack example Assembly program

# Following instructions printout the alphabet
# Directive .start contains starting point (ASCII-code of A)
# Directive .end contains ending point (ASCII-code of Z)

.start db 65
.end db 91

# Load the starting ASCII value into TOS
mov .start

.loop
# Duplicate it for the comparison
dup

# Check if we have already finished printing the alphabet
cmpe .end

# Jump to the end of the program if we are finished with printing
jc .finish

# Output TOS value to the device at port 1
dup
out $1

# Increment the value of the ASCII code by 1
mov $1
add

# Jump back to the start of the loop
jmp .loop

.finish
# Finish program
nop