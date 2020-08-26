# Alphabet Printout | Register-RISC example Assembly program

# Following instructions printout the alphabet
# Directive .start contains starting point (ASCII-code of A)
# Directive .end contains ending point (ASCII-code of Z)

.start db 65
.end db 91

# Load the starting point of the loop (and an ASCII code) into the register R00
mov_low %R00, .start

# Load the number 1 into the register %R01 to use as an incrementer in the loop
mov_low %R01, $1

# Load the finishing point of the loop (and an ASCII code) into the register R02
mov_low %R02, .end

.loop
# This 'compare' instruction subtracts R00's value from R02 and uses the Flag Register to describe the result
cmp %R02, %R00

# This 'jump equal' instruction checks if the result of 'cmp' was zero, and if it was,
# jumps to the .finish (4 instructions forward in that example) to the end of the program to skip the loop
je .finish

# This 'out' instruction transmits the value of the register R00 to the device at port 1
out $1, %R00

# This add instruction saves the result of the R00+R01 operation into the first operand - R00
# This way, we increase the R00's value and go to the next ASCII character
add %R00, %R00, %R01

# This jump instruction always jumps to the .loop (4 instructions back in that example), to the start of the loop - the 'cmp' instruction
jmp .loop

.finish
# Finish the program
nop