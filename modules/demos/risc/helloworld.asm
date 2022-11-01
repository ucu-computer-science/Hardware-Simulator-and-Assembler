# Hello World PrintOut | Register-RISC example Assembly program
# These next instructions load ASCII encodings of characters in "Hello world!" into registers
# and then push them onto the stack, backwards, so that when the values are popped from the stack,
# we can output the values in a normal way
 
mov_low %R00, $33   # mov_low %R00, $33 
push %R00
mov_low %R00, $100
push %R00
mov_low %R01, $108
push %R01
mov_low %R00, $114
push %R00
mov_low %R02, $111
push %R02
mov_low %R00, $119
push %R00
mov_low %R00, $32
push %R00
push %R02
push %R01
push %R01
mov_low %R00, $101
push %R00
mov_low %R00, $72
push %R00

# These instructions establish the loop, with R00 containing the starting value,
# R01 - the value R00 is going to be incremented on each loop iteration
# R02 - The finishing point of the loop we are checking against
mov_low %R00, $1
mov_low %R01, $1
mov_low %R02, $13

# This 'compare' instruction subtracts R00's value from R02 and uses the Flag Register to describe the result
cmp %R02, %R00

# This 'jump equal' instruction checks if the result of 'cmp' was zero, and if it was,
# jumps to the .finish (5 instructions forward in that example) to the end of the program to skip the loop
je .finish

# Inside the loop, we pop the value from the memory stack to R03 register, and output it into the device at port 1
pop %R03
out $1, %R03

# This add instruction saves the result of the R00+R01 operation into the first operand - R00
# This way, we increase the R00's value and go to the next loop iteration
add %R00, %R00, %R01

# This unconditional jump instruction transitions to the start of the loop
jmp $-5

.finish
# Finish the program
nop