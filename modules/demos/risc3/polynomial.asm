# Polynomial Calculation | Register-RISC example Assembly program

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
mov_low %R03, .start
mov_low %R02, .n


# Evaluation loop:
.evalloop
# Store current info in registers
mov_low %R00, $1
mov %R01, %R02

.powerloop
# If current power is less than 1, skip to multiplying by coefficient
cmp %R01, $1
jl .multcoef

# Raise value of x to the current power
push %R01
mov_low %R01, .value
mul %R00, %R00, %R01
pop %R01
push %R02
mov_low %R02, $1
sub %R01, %R01, %R02
pop %R02
jmp .powerloop

.multcoef
# Multiply by the coefficient
load %R01, [%R03]
mul %R00, %R00, %R01

# Push result into memory
push %R00

# Check if we are finished with going through the coefficients list
push %R01
mov_low %R01, $2
add %R03, %R03, %R01
pop %R01
cmp %R03, .end
je .additionloop

# If not, decrement power and continue going through the list
push %R01
mov_low %R01, $1
sub %R02, %R02, %R01
pop %R01
jmp .evalloop


# Addition loop:
.additionloop
# Add all the evaluated values and store result in memory
mov_low %R00, $0

.addition
pop %R01
add %R00, %R00, %R01
cmp %R03, .start
je .storing

push %R01
mov_low %R01, $2
sub %R03, %R03, %R01
pop %R01
jmp .addition

# Store result value
.storing
mov_low %R01, .resultindex
mov_high %R01, .resultindex
store [%R01], %R00

# Finish the program
nop