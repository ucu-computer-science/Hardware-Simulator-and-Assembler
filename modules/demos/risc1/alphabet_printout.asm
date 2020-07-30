# Load the starting ASCII value into TOS
mov $65

# Duplicate it for the comparison
dup

# Check if we have already finished printing the alphabet
cmpe $91

# Jump to the end of the program if we are finished with printing
jc $6

# Output TOS value to the device at port 1
dup
out $1

# Increment the value of the ASCII code by 1
mov $1
add

# Jump back to the start of the loop
jmp $-7