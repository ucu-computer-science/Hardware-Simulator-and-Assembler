# Bubble Sort | Accumulator-RISC example Assembly program

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
# Push 'zero' change indicator
mov $0
push

# Load starting point
mov .start
storei

.loop
# Jump to the indicator check, if the list was finished
loadi
cmp .end
je .checkcondition

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
jle .loop

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
jmp .loop

.checkcondition
# Check if there were any changes, finish if not
mov $0
storei
pop
cmp $0
jne .listloop

# Finish the program
nop
