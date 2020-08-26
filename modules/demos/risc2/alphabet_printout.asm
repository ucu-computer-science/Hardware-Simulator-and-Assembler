# Alphabet PrintOut | Accumulator-RISC example Assembly program

# Following instructions printout the alphabet
# Directive .start contains starting point (ASCII-code of A)
# Directive .end contains ending point (ASCII-code of Z)

.start db 65
.end db 91

# Load the starting ASCII value into ACC
mov .start

.loop
# Check if we have already finished printing the alphabet
cmp .end

# Jump to the end of the program if we are finished with printing
je .finish

# Output ACC value to the device at port 1
out $1

# Increment the value of the ASCII code by 1
inc

# Jump back to the start of the loop
jmp .loop

.finish
# Finish program
nop
