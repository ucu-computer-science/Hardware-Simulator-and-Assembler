# Bubble Sort | Register-CISC example Assembly program

# These instructions sort a manually 'created' list with three values
# Manually write three values into the memory (in the very start)
# Example: 00 30 00 20 00 10 00 00
# Result should be: 00 10 00 20 00 30 00 00

# R02 register contains current index of the
# R03 is used as changes indicator

.mainloop
# Load two values into registers
mov %R00, $0
add %R00, [%R02]
mov %R01, $0
add %R01, [%R02+$2]

# Compare them
cmp %R00, %R01

# If they are in the right order –– skip swapping them
jle .continue

# Swapping
push %R00
mov %R00, %R01
pop %R01
mov %R03, $1

.continue
push %R01
push %R00
inc %R02
inc %R02
cmp %R02, $6
jne .mainloop

# TODO: check if anything has changed
nop