# Alphabet PrintOut | Register-CISC example Assembly program

# Load starting point (ASCII-code of A)
mov %R00, $65

# Load ending point (ASCII-code of Z)
mov %R01, $91

# Main printout loop
.mainloop
# Printout the letter and increment register's value
out $1, %R00
inc %R00

# Check if program finished the whole alphabet
cmp %R00, %R01
jle .mainloop

# Finish program
nop