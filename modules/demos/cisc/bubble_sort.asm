# Bubble Sort | Register-CISC example Assembly program

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
# R02 register contains current index of the list
# R03 is used as changes indicator (bubble sort is finished when no changes are present)
mov %R02, .start
mov %R03, $0

.mainloop
# Load two values into registers (step is two bytes, for it is the length of the word)
mov %R00, [%R02]
mov %R01, [%R02+$2]

# Compare them
cmp %R00, %R01

# If they are in the right order –– skip swapping them
jle .continue

# Swapping
push %R00
mov %R00, %R01
pop %R01

# Changing values in the memory
mov [%R02], %R00
mov [%R02+$2], %R01

# Set indicator to True
mov %R03, $1

# Check if we finished going through the list
.continue
mov %R00, $2
add %R02, %R00
cmp %R02, .end
jne .mainloop

# Check if anything has changed in the list: if it did, go through the list once again
cmp %R03, $1
je .listloop

# Finish the program
nop