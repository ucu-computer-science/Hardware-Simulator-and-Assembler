# Polynomial Calculation | Stack example Assembly program

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
.indexn db 10
.indexnewn db 12
.value db 2
.resultindex db 0

# Store maxvalue of n by chosen index
mov .indexn
store .n

# Push the first index of coefficients list to memory
mov .start
push

.mainloop
# Check if we have finished going through the list
pop
dup
push
cmpb .end
jc .additionloop

mov .indexnewn
mov .indexn
load
store


.loop
# Check if n > 0
mov .indexnewn
load
cmpb $0
jc $2

# Multiply values
jmp .continue
pop
dup
dup
push
load
mov .value
mul
store

# Decrement current value of n
mov .indexnewn
dup
load
mov $-1
add
store
jmp .loop

.continue
pop
mov $2
add
push
mov .indexn
dup
load
mov $-1
add
store
jmp .mainloop

# Add resulting values
.additionloop
mov .resultindex
mov $0

.addition
pop
dup
push
cmpe .start
jc .finishaddition
pop
mov $-2
add
dup
push
load
add
jmp .addition

# Store the result
.finishaddition
store

# Finish the program
nop