import os

isas = ['stack', 'accumulator', 'risc', 'cisc']
# Example program variants:
alphabets = []
hellos = []
bubble_sorts = []
polynomials = []
simd = ''

for isa in isas:
    try:
        with open(os.path.join("modules", "demos", isa, "alphabet_printout.asm"), 'r') as file:
            program = file.read()
        alphabets.append(program)
    except FileNotFoundError:
        alphabets.append('Coming soon...')
    try:
        with open(os.path.join("modules", "demos", isa, "helloworld.asm"), 'r') as file:
            program = file.read()
        hellos.append(program)
    except FileNotFoundError:
        hellos.append('Coming soon...')
    try:
        with open(os.path.join("modules", "demos", isa, "bubble_sort.asm"), 'r') as file:
            program = file.read()
        bubble_sorts.append(program)
    except FileNotFoundError:
        bubble_sorts.append('Coming soon...')
    try:
        with open(os.path.join("modules", "demos", isa, "polynomial.asm"), 'r') as file:
            program = file.read()
        polynomials.append(program)
    except FileNotFoundError:
        polynomials.append('Coming soon...')

    # SIMD for CISC
    try:
        with open(os.path.join("modules", "demos", isa, "helloworld_simd.asm"), 'r') as file:
            simd = file.read()
    except FileNotFoundError:
        simd = 'Coming soon...'

stack_examples = [alphabets[0], hellos[0], bubble_sorts[0], polynomials[0], 'input assembly code here']
accumulator_examples = [alphabets[1], hellos[1], bubble_sorts[1], polynomials[1], 'input assembly code here']
risc_examples = [alphabets[2], hellos[2], bubble_sorts[2], polynomials[2], 'input assembly code here']
cisc_examples = [alphabets[3], hellos[3], bubble_sorts[3], polynomials[3], simd]

# That dictionary is used later in the web app
examples = {'stack': stack_examples, 'accumulator': accumulator_examples, 'risc': risc_examples, 'cisc': cisc_examples}
