# Bubble Sort | Stack-RISC example Assembly program

# NOT FINISHED!!!

# These instructions sort a manually 'created' list
# Directive .start contains the starting index of the list (0 in that example)
# Directive .end contains the ending index of the list (6 in that example)
# Values must be manually written into the data memory after the program was assembled
# Example list: 00 30 00 20 00 10 00 00
# Result will be: 00 00 00 10 00 20 00 30

# Directives:
.start db 0
.end db 6

# Add first index to stack
mov .start

.loadingloop
# Add value from the list at that index
dup
push
load
pop

# Add next index to stack
mov $2
add

# Check if the list has finished (in this example we use 3-bytes list)
dup
cmpe .end
jc .swaploop

# Continue going through the list
jmp .loadingloop

.swaploop
# Move to the start of the list
push
push
push
push