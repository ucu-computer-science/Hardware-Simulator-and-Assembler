# Polynomial Calculation | Register-CISC example Assembly program

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

# Store initial info in registers
mov %R03, .start
mov %R02, .n


# Evaluation loop:
.evalloop
# Store current info in registers
mov %R00, $1
mov %R01, %R02

.powerloop
# If current power is less than 1, skip to multiplying by coefficient
cmp %R01, $1
jl .multcoef

# Raise value of x to the current power
mul %R00, .value
dec %R01
jmp .powerloop

.multcoef
# Multiply by the coefficient
mov %R01, [%R03]
mul %R00, %R01

# Push result into memory
push %R00

# Check if we are finished with going through the coefficients list
inc %R03
inc %R03
cmp %R03, .end
je .additionloop

# If not, decrement power and continue going through the list
dec %R02
jmp .evalloop


# Addition loop:
.additionloop
# Add all the evaluated values and store result in memory
mov %R00, $0

.addition
pop %R01
add %R00, %R01
cmp %R03, .start
je .storing
dec %R03
dec %R03
jmp .addition

# Store result value
.storing
mov %R01, .resultindex
mov [%R01], %R00

# Finish the program
nop