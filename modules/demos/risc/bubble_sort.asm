# Bubble Sort | Register-RISC example Assembly program

# These instructions sort a manually 'created' list
# Directive .start contains the starting index of the list (0 in that example)
# Directive .end contains the ending index of the list (6 in that example)
# Values must be manually written into the data memory after the program was assembled
# Example list: 00 30 00 20 00 10 00 00
# Result will be: 00 00 00 10 00 20 00 30

# Directives:
.start db 0
.end db 6

.listloop
# Step (2 bytes)
mov_low %R03, $2
# Set start of the loop
mov_low %R02, .start
# Set change indicator to zero
mov_low %R00, $0
push %R00

.mainloop
# Load first value
load %R00, [%R02]
add %R02, %R02, %R03
# Load second value
load %R01, [%R02]

# If the first value is less-equal than second, continue moving through the list
cmp %R00, %R01
jle .continue

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
push %R03

.continue
# If the list was not finished, continue going through it
cmp %R02, .end
jl .mainloop


# If there is no an indicator in the memory –– finish program,
# otherwise start going through the list once again
mov_low %R00, $0
pop %R00
cmp %R00, %R03
je .listloop

.finish
#Finish the program
nop