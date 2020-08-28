# Polynomial Calculation | Accumulator-RISC example Assembly program

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