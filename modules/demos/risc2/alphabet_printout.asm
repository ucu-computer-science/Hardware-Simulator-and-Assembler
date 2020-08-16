# Alphabet PrintOut | Accumulator-RISC example Assembly program
# Load the starting ASCII value into ACC
mov $65

# Check if we have already finished printing the alphabet
cmp $91

# Jump to the end of the program if we are finished with printing
je $4

# Output ACC value to the device at port 1
out $1

# Increment the value of the ASCII code by 1
inc

# Jump back to the start of the loop
jmp $-4
