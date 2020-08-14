# Alphabet PrintOut | Accumulator-RISC example Assembly program
# Load the starting ASCII value into TOS
mov $65
push
cmp $91
je $6
pop
out $1
inc
jmp $-6