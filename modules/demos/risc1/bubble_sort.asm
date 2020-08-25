# Bubble Sort | Stack-RISC example Assembly program

# Example list: 00 30 00 20 00 10 00 00
# Add first index to stack
mov $0

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
cmpe $6
jc $2

# Continue going through the list
jmp .loadingloop

.swaploop
# Move to the start of the list
push
push
push
push