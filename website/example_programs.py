import os

isas = ['risc1', 'risc2', 'risc3', 'cisc']
alphabets = []
hellos = []

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

risc1_examples = [alphabets[0], hellos[0]]
risc2_examples = [alphabets[1], hellos[1]]
risc3_examples = [alphabets[2], hellos[2]]
cisc_examples = [alphabets[3], hellos[3]]

examples = {'risc1': risc1_examples, 'risc2': risc2_examples, 'risc3': risc3_examples, 'cisc': cisc_examples}
