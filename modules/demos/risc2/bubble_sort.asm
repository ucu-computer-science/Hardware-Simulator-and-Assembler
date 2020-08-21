# Bubble Sort | Accumulator-RISC example Assembly program
# These instructions sort a manually 'created' list with three values
# Manually write three values into the memory (in the very start)
# Example: 00 30 00 20 00 10 00 00
# Result should be: 00 10 00 20 00 30 00 00

# Push 'zero' change indicator
mov $0
push

# Jump to the end, if the list was finished
loadi
cmp $4
je $29

# Compare two values
load
push

# There is a step (2 bytes)
loadi
inc
inc
storei

pop
cmp

# If the first value is less/equal than second, continue going through the list
jle $-11

# If it is bigger, swap values
push
load
push

loadi
dec
dec
storei

pop
store

loadi
inc
inc
storei

pop
store

# Push change indicator
pop
mov $1
push

# Continue going through the list
jmp $-30

# Check if there were any changes, finish if not
mov $0
storei
pop
cmp $0
jne $-37

# Finish the program
nop
