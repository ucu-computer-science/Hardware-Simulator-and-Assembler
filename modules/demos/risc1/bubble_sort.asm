# Bubble Sort | Stack-RISC example Assembly program

# These instructions sort a manually 'created' list
# Directive .start contains the starting index of the list (0 in that example)
# Directive .end contains the ending index of the list (6 in that example)
# Directive .indicator contains the address, where changes indicator will be stored (10 in that example)
# Values must be manually written into the data memory after the program was assembled
# Example list: 00 30 00 20 00 00 00 10
# Result will be: 00 00 00 10 00 20 00 30

# Directives:
.start db 0
.end db 6
.indicator db 10

.listloop
mov $0
push
# Change indicator to False
mov .indicator
store $0
# Add first index to stack
mov .start

.loop
# Save index and load value from list
dup
push
dup
push
load

# Pop previous index, add 2 to it and load next value
pop
mov $2
add
dup
push
load

# Compare two values and swap them if needed
cmpb
jc .continue

# Swap
pop
dup
mov $-2
add
load
pop
dup
mov $2
add
dup
dup
push
push
load
store
store
# Change indicator to true
mov .indicator
store $1

.continue
pop
dup
push
cmpe .end
jc .checkcondition
pop
jmp .loop

.checkcondition
mov .indicator
load
cmpe $1
jc .listloop

# Finish the program
nop