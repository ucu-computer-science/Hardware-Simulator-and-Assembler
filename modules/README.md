## Modules structure

* `simulator.py` - the main Hardware Simulator module also using:
    * `memory.py` - memory simulator class
    * `register.py` - CPU register simulator class
    * `functions.py` - functions definitions for all the binary code instructions
    * `program_examples` - contains binary code program examples:
        * `move_add.bin` - basic test of the `mov` instruction for registers and constants, `add` between registers for RISC-Register architecture

* `instruction.json` - a list of opcodes and operands for every possible instruction for every architecture. Is used by both the assembler and simulator
* `registers.json` - a list of registers and their encodings for every architecture