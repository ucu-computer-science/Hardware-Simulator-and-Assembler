# Manually write three values into the memory (in the very start)
# Example: 00 30 00 20 00 10 00 00
# Result should be: 00 10 00 20 00 30 00 00

# Step (2 bytes)
mov_low %R03, $2
# Set change indicator to zero
push %R00


# Load first value
load %R00, [%R02]
add %R02, %R02, %R03
# Load second value
load %R01, [%R02]


# If the list was finished move to the end
cmp %R02, $6
je $13

# If the first value is less-equal than second, continue moving through the list
cmp %R00, %R01
jle $-6

# If it is bigger, swap values
push %R00
mov %R00, %R01
pop %R01

# Store changes in the memory
sub %R02, %R02, %R03
store [%R02], %R00
add %R02, %R02, %R03
store [%R02], %R01
# Change indicator in the memory
pop %R00
push %R02
jmp $-16


# If there is no an indicator in the memory –– finish program
mov_low %R00, $0
pop %R00
cmp %R00, %R01
je $5

# If there was an indicator in the memory, push a zero value and continue
mov_low %R02, $0
push %R02
jmp $-23

#Finish the program
nop