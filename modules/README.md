## Modules structure

* `processor.py` - the main Hardware Simulator module also using:
    * `memory.py` - memory simulator class
    * `register.py` - CPU register simulator class
    * `shell.py` - the class for our only 'device' - the shell
    * `functions.py` - functions definitions for all the binary code instructions
    * `program_examples/` - contains binary code program examples, some are self-explanatory, 
    some are not and nobody knows why they exist
    * `demos/` - contains somewhat more user-oriented program examples,
    which are indeed the 'program examples' on the website

* `assembler.py` - the Assembler, both the main module and CL interface for it

* `simulator.py` - the module for CLI usage of the Hardware Simulator
* `instructions.json` - a list of opcodes and operands for every possible instruction for every architecture. 
Is used by both the assembler and simulator
* `registers.json` - a list of registers and their encodings for every architecture