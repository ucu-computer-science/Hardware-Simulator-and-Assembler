# Alphabet PrintOut | Register-CISC example Assembly program

# Following instructions printout the alphabet
# Directive .start contains starting point (ASCII-code of A)
# Directive .end contains ending point (ASCII-code of Z)

.start db 65
.end db 91

# Load starting point
mov %R00, .start

# Main printout loop
.mainloop
# Printout the letter and increment register's value
out $1, %R00
inc %R00

# Check if program finished printing out the whole alphabet
cmp %R00, .end
jle .mainloop

# Finish program
nop