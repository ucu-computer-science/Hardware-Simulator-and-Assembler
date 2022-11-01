# Polynomial Calculation | Accumulator example Assembly program

# These instructions calculate a value of a polynomial expression
# In that example polynomial is 2*x^2 + 3*x - 7, x = 2
# Answer will be 7

# Directive .start contains the starting index of the list with coefficients (2 in that example)
# Directive .end contains the ending index of the list with coefficients (6 in that example)
# Directive .n contains maximum power of the polynomial expression (2 in that example)
# Directive .value contains maximum power of the variable (2 in that example)
# Directive .resultindex contains address, where result will be stored (0 in that example)


# Coefficients must be manually written into the data memory after the program was assembled
# Example list of coefficients: 00 02 00 03 ff f9

# Directives:
.start db 2
.end db 6
.n db 2
.value db 2
.resultindex db 0

# Load initial start index to IR
mov .start
storei

# Push maximum power of the expression
mov .n
push
push

# Go through coefficients in the list
.listloop
loadi
cmp .end
jg .startaddition

# Work with each coefficient
.powerloop
pop

# Skip multiplication if power is less than 1
cmp $1
jl .finishpowerloop
dec
push
mov .value
mul
store
jmp .powerloop

# Finish with raising value to the power
.finishpowerloop
pop
dec
push
push
loadi
inc
inc
storei
jmp .listloop

# Add values in the list
.startaddition
mov $0
push

.additionloop
loadi
cmp .start
je .result
dec
dec
storei
pop
add
push
jmp .additionloop

# Store the result in the memory
.result
mov .resultindex
storei
pop
store

# Finish the program
nop