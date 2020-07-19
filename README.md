# POC Project: Instruction sets simulation and assembly

---

## Description:

### Project goals: :cherry_blossom:

* Create simple instruction sets, which will belong to different architectures
(which are listed below)

* Create a simulator (to see differences in these architectures)

* Create a (simple) assembly language for others to use

## Architectures:

* Instruction Set Architecture (Register Architecture)

  1. Stack (Zero-Address)

  2. Accumulator (One-Address)

  3. Register (Two-Address)

* Instruction Set Complexity

  1. Reduced Instruction Set Computer (RISC)
  
  2. Complex Instruction Set Computer (CISC)

* General Architecture

  1. Von Neumann (Princeton) architecture

  2. Harvard architecture
  
  3. Modified Harvard architecture

* Input/Output

  1. Memory-Mapped I/O
  
  2. Separate Space MMIO
  
  3. Special commands

+ SIMD


### What we will (possibly) use: :maple_leaf:

* Python

* [Dominate](https://github.com/Knio/dominate) for generating HTML pages

### Examples and resources: :fallen_leaf:

* Guidelines from [nand2tetris](http://f.javier.io/rep/books/The%20Elements%20of%20Computing%20Systems.pdf)

* https://schweigi.github.io/assembler-simulator/

* https://parraman.github.io/asm-simulator/

---

## Usage

```bash
git clone https://github.com/dariaomelkina/poc_project
# Assembler:
python3 modules/assembler.py -f modules/program_examples/assembly_test.asm --isa RISC3
# Simulator:
python3 modules/simulator.py --file modules/program_examples/move_add.bin --isa RISC3 --architecture Harvard
```

---

## Prerequisites:

```bash
pip install -r requirements.txt
```
---

## Testing:

---

## Credits:

---

## License:

GNU General Public License v3.0