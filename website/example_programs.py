import os

isas = ['risc1', 'risc2', 'risc3', 'cisc']
# Example program variants:
alphabets = []
hellos = []
bubble_sorts = []
polynomials = []

for isa in isas:
    try:
        with open(os.path.join("modules", "demos", isa, "alphabet_printout.asm"), 'r') as file:
            program = file.read()
        alphabets.append(program)
    except FileNotFoundError:
        alphabets.append('')
    try:
        with open(os.path.join("modules", "demos", isa, "helloworld.asm"), 'r') as file:
            program = file.read()
        hellos.append(program)
    except FileNotFoundError:
        hellos.append('')
    try:
        with open(os.path.join("modules", "demos", isa, "bubble_sort.asm"), 'r') as file:
            program = file.read()
        bubble_sorts.append(program)
    except FileNotFoundError:
        bubble_sorts.append('')
    try:
        with open(os.path.join("modules", "demos", isa, "polynomial.asm"), 'r') as file:
            program = file.read()
        polynomials.append(program)
    except FileNotFoundError:
        polynomials.append('')

risc1_examples = [alphabets[0], hellos[0], bubble_sorts[0], polynomials[0]]
risc2_examples = [alphabets[1], hellos[1], bubble_sorts[1], polynomials[1]]
risc3_examples = [alphabets[2], hellos[2], bubble_sorts[2], polynomials[2]]
cisc_examples = [alphabets[3], hellos[3], bubble_sorts[3], polynomials[3]]

# That dictionary is used later in the web app
examples = {'risc1': risc1_examples, 'risc2': risc2_examples, 'risc3': risc3_examples, 'cisc': cisc_examples}
