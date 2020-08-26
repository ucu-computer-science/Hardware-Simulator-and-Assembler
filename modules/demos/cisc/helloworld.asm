# Hello World PrintOut | Register-CISC example Assembly program

# That option of the program is aimed to printout 'Hello World!',
# showing how CISC instructions might appear easier for user (and faster)
# Directive .length contains number of elements in the string 'Hello World!'

.length db 12

# Push letters (ASCII-codes) into the memory
push $33
push $100
push $108
push $114
push $111
push $119
push $32
push $111
push $108
push $108
push $101
push $72


# Main loop for printing out letters
.loop
pop %R03
out $1, %R03

# Increment counter and check if we are finished going through the string
inc %R00
cmp %R00, .length
jl .loop

# Finish the program
nop