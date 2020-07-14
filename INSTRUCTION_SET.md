# Instruction Set:

* % –– register (```%reg```)
* [] –– memory location (```[mem]```)
* $ –– constant value (```$42```)

All instructions are 16-bit. As we have 32 instructions, we require 5 bits to represent the opcode, with 11 bits left for zero, one or two operands.

- - -

Using Intel-style instructions with results of computations
being saved into the first operand:

```operation destination, <----- source ```

- - -

*We are not using direct memory access unless we have to (like in accumulator architecture).
This emphasizes the complexity of CISC instructions and eases the actual programming*

- - -

## Registers that are included in every architecture:

* ### Flag register:
    * Carry flag ```CF```
    * Zero flag ```ZF```
    * Overflow flag ```OF```
    * Sign flag ```SF```

* ### Memory stack registers:
    * Stack pointer ```esp```
    * Stack base pointer ```ebp```

- - -

## Instructions for each architecture with short descriptions

| RISC STACK | RISC ACCUMULATOR | RISC REGISTER | CISC REGISTER |
|------------|------------------|---------------|---------------|
| **Registers** ||||
| ```tos``` - Points to the top of the register stack in the memory| ```acc``` - Points to the accumulator register*| *```A``` - General-purpose 16-bit word; ```BC``` - General-purpose 16-bit word, B-high byte, C-low byte; ```DE``` - General-purpose 16-bit word, D-high byte, E-low byte; ```FG``` - General-purpose 16-bit word, F-high byte, G-low byte* | *```A``` - General-purpose 16-bit word; ```BC``` - General-purpose 16-bit word, B-high byte, C-low byte; ```DE``` - General-purpose 16-bit word, D-high byte, E-low byte; ```FG``` - General-purpose 16-bit word, F-high byte, G-low byte* |
| | | | |
| **Memory** |   |   |   |
| ```load [mem]``` | ```load [mem]``` | ```load %reg, [mem]``` | ```load %reg, [mem]``` |
| *Loads word from memory at location ```mem``` and pushes into the memory on ```tos```* | *Loads word from memory at location ```mem``` into an ```acc``` register* | *Loads word from memory at location ```mem``` into register ```reg```* |  *Loads word from memory at location ```mem``` into register ```reg```* |
|||||
| ```store [mem]``` | ```store [mem]``` | ```store [mem], %reg``` | ```store [mem], %reg``` |
| *Pops the word from ```tos``` and stores it in the memory at location ```mem```* | *Copies word from the ```acc``` register and stores it in the memory at location ```mem```* | *Copies word from the register ```reg``` and stores it in memory  at location ```mem```* | *Copies word from the register ```reg``` and stores it in memory  at location ```mem```* |
|||||
| | | ```mov %reg1, %reg2``` | ```mov %reg1, %reg2``` |
| | | *Copies the value of ```reg2``` into ```reg1```* | *Copies the value of ```reg2``` into ```reg1```* |
|||||
| ```push``` | ```push``` | ```push %reg``` | ```push %reg``` |
| *Pops the ```tos```, pushes the value into the memory stack* | *Pushes the value of the ```acc``` register on to the top of the memory stack* | *Pushes the value of ```reg``` on the top of the memory stack* | *Pushes the value of ```reg``` on the top of the memory stack* |
|||||
| ```pop``` | ```pop``` | ```pop %reg``` | ```pop %reg``` |
| *Pops the previous value of ```tos``` from the memory stack and pushes on top of the register stack* | *Pops the previous value of ```acc``` from the memory stack into ```acc```* | *Pops previous value of ```reg``` from the memory stack into ```reg```* | *Pops previous value of ```reg``` from the memory stack into ```reg```* |
|||||
| | | | ```enter $num``` |
|||| *Replaces three instructions on moving the stack further down when calling a new procedure: ```push %ebp / mov %ebp, %esp / sub %esp, $num``` Notice you still have to push the other registers onto the memory stack*|
|||||
| | | | ```leave``` |
|||| *Replaces two instructions when returning to the previous procedure's stack frame: ```mov %esp, %ebp / pop %ebp```*|
| | | | |
| **Arithmetic** |   |   |   |
| ```add``` | ```add [mem]``` | ```add %reg1, %reg2``` | ```add %reg, [mem]``` |
| | ```add %acc```| | ```add [mem1], [mem2]``` |
| *Pops two items from ```tos```, adds their values, pushing the result into the register on ```tos```* | *Add items from the ```acc``` register and memory location ```mem``` (or ```acc``` register), pushing the result into ```acc```* | *Adds items at register ```reg``` and memory location ```mem```, saving the result at ```reg```* | *Adds items at register ```reg``` (or memory location ```mem1```) and memory location ```mem``` (or memory location ```mem2```), saving the result at ```reg``` (or memory location ```mem1```)* |
|||||
| ```sub``` | ```sub [mem]``` | ```sub %reg1, %reg2``` | ```sub %reg, [mem]``` |
|  | ```sub %acc``` |  | ```sub [mem1], [mem2]``` |
| *Pops two items from ```tos```, subtracting the second one from the first, and pushes the result into the register on ```tos```* | *Subtracts value stored at location ```mem``` (or register ```acc```) from value stored in ```acc``` register, saving the result in the ```acc``` register* | *Subtracts value at the memory location ```mem``` from the register ```reg```, saving the result in the register ```reg```* | *Subtracts value at the memory location ```mem``` (or at memory location ```mem1```) from the register ```reg``` (or from memory location ```mem1```), saving it in the register ```reg``` (or at the memmory location ```mem1```)* |
|||||
| ```inc``` | ```inc [mem]``` | ```inc %reg``` | ```inc %reg``` |
|  | ```inc %acc``` |  | ```inc [mem]``` |
| *Pops the value from ```tos```, increments it, and pushes on ```tos```*| *Increments value from the register ```acc```, saving it in the register ```acc```* | *Increments value from the register ```reg```, saving the result in the register ```reg```* | *Increments value from the register ```reg``` (or at the location ```mem```), saving the result in the register ```reg``` (or at the location ```mem```)* |
|||||
| ```dec``` | ```dec [mem]``` | ```dec %reg``` | ```dec %reg``` |
|  |  |  | ```dec [mem]``` |
| *Pops the value from ```tos```, decrements it, and pushes on ```tos```* | *Decrements value from the register ```acc```, saving it in the register ```acc```* | *Decrements value from the register ```reg```, saving the result in the register ```reg```* | *Decrements value from the register ```reg``` (or at the location ```mem```), saving the result in the register ```reg``` (or at the location ```mem```)* |
|||||
| ```mul``` | ```mul [mem]``` | ```mul %reg1, %reg2``` | ```mul %reg1, %reg2``` |
| | | | ```mul %reg, [mem]```|
| *Pops two items from ```tos```, multiplies them, and pushes the result into ```tos```* | *Multiplies value from the location ```mem``` and value from the register ```acc```, saving the result in the register ```acc```* | *Multiplies value from the register ```reg1``` and value from the register ```reg2```, saving the result in the register ```reg1```* | *Multiplies value from the register ```reg1```(from the register ```reg```) and value from the register ```reg2```(at location ```mem```), saving the result in the register ```reg1```(in the register ```reg```)* |
|||||
| ```div``` | ```div [mem]``` | ```div %reg1, %reg2``` | ```div %reg1, %reg2``` |
|  |  |  | ```div %reg, [mem]``` |
| *Pops two items from ```tos```, dividing the first one by the second, and pushes the result into ```tos```* | *Divides value from the register ```acc``` by value at the location ```mem```, saving the result in the register ```acc```* | *Divides value from the register ```reg1``` by value from the register ```reg2```, saving the result in the register ```reg1```* | *Divides value from the register ```reg1``` (or the register ```reg```) by value from the register ```reg2```(or at location ```mem```), saving the result in the register ```reg1```(or in the register ```reg```)* |
|  |  |  |  |
| **Logical** |   |   |   |
| ```and``` | ```and [mem]``` | ```and %reg1, %reg2``` | ```and %reg1, %reg2``` |
|  |  |  | ```and %reg, [mem]``` |
| *Computes binary ```and``` between two popped values from the stack, pushes the result on to the ```tos```* | *Computes binary ```and``` between word from the ```acc``` register and ```mem``` location, saving the result into ```acc```* | *Computes binary ```and``` between ```reg1``` and ```reg2``` and saves the result into ```reg1```* | *Computes binary ```and``` between ```reg1``` and ```reg2``` (or ```mem``` location) and saves the result into ```reg1``` (or into ```reg```)* |
|||||
| ```or``` | ```or [mem]``` | ```or %reg1, %reg2``` | ```or %reg1, %reg2``` |
| | | | ```or %reg, [mem]``` |
| *Computes binary ```or``` between two popped values from the stack, pushes the result on to the ```tos```* | *Computes binary ```or``` between word from the ```acc``` register and ```mem``` location, saving the result into ```acc```* | *Computes binary ```or``` between ```reg1``` and ```reg2``` and saves the result into ```reg1```* | *Computes binary ```or``` between ```reg1``` and ```reg2``` (or ```mem``` location) and saves the result into ```reg1``` (or into ```reg```)* |
|||||
| ```xor``` | ```xor [mem]``` | ```xor %reg1, %reg2``` | ```xor %reg1, %reg2``` |
| |  |  | ```xor %reg, [mem]``` |
| *Computes binary ```xor``` between two popped values from the stack, pushes the result on to the ```tos```* | *Computes binary ```xor``` between word from the ```acc``` register and ```mem``` location, saving the result into ```acc```* | *Computes binary ```xor``` between ```reg1``` and ```reg2``` and saves the result into ```reg1```* | *Computes binary ```xor``` between ```reg1``` and ```reg2``` (or ```mem``` location) and saves the result into ```reg1``` (or into ```reg```)* |
| | | | |
| **Shifts** | | | |
| ```lsh $num``` | ```lsh $num``` | ```lsh %reg, $num``` | ```lsh %reg, $num``` |
|  |  |  | ```lsh [mem], $num``` |
| *Pops value from the ```tos```, shifts it by ```num``` to the left, and pushes the result on to ```tos```* | *Shifts the value from register ```acc``` by ```num``` to the left, saving the result in the register ```acc```* | *Shifts the value from register ```reg``` by ```num``` to the left, saving the result in the register ```reg```* | *Shifts the value from register ```reg``` (or at location ```mem```) by ```num``` to the left, saving the result in the register ```reg```(or at location ```mem```)* |
|||||
| ```rsh $num``` | ```rsh $num``` | ```rsh %reg, $num``` | ```rsh %reg, $num```|
|  |  |  | ```rsh [mem], $num```|
| *Pops value from the ```tos```, shifts it by ```num``` to the right, and pushes the result on to ```tos```* | *Shifts the value from register ```acc``` by ```num``` to the right, saving the result in the register ```acc```* | *Shifts the value from register ```reg``` by ```num``` to the right, saving the result in the register ```reg```* | *Shifts the value from register ```reg``` (or at location ```mem```) by ```num``` to the right, saving the result in the register ```reg``` (or at location ```mem```)* |
| | | | |
| **Flow control** |   |   |   |
| ```call label``` | ```call label``` | ```call label``` | ```call label``` |
| ```call $num``` | ```call $num``` | ```call $num``` | ```call $num``` |
| ```call``` | ```call``` | ```call %reg``` | ```call %reg``` |
| *Pushes the next instruction's location on to the memory stack, transfers control to the location at ```num``` or at ```tos```* | *Pushes the next instruction's location on to the memory stack, transfers control to the location at ```num``` or ```acc```* | *Pushes the next instruction's location on to the memory stack, transfers control to the location at ```num``` or ```reg```* | *Pushes the next instruction's location on to the memory stack, transfers control to the location at ```num``` or ```reg```* |
|||||
| ```ret``` | ```ret``` | ```ret``` | ```ret``` |
| *Transfers control to the popped instruction location* | *Transfers control to the popped instruction location* | *Transfers control to the popped instruction location* | *Transfers control to the popped instruction location* |
|||||
| ```cmp``` | ```cmp [mem]``` | ```cmp %reg1, %reg2``` | ```cmp %reg1, %reg2``` |
| ```cmp $num``` | ```cmp $num``` | ```cmp %reg, $num``` | ```cmp %reg, $num``` |
|  |  |  | ```cmp %reg, [mem]``` |
| *Compares two numbers on ```tos``` by subtracting the second one from the first one, changing the flags accordingly (or compares value from the top register with a constant ```num```)* | *Compares value of register ```acc``` and value at location ```mem``` (or with constant ```num```), by subtracting the second one from the first one, changing the flags accordingly* | *Compares value of register ```reg1```(or ```reg```) and value of register ```reg2``(or with constant ```num```)`, by subtracting the second one from the first one, changing the flags accordingly* | *Compares value of register ```reg1```(or ```reg```) and value of register ```reg2```(or at ```mem```) or constant ```num```, by subtracting the second one from the first one, changing the flags accordingly* |
|||||
| ```test $num``` | ```test $num``` | ```test %reg1, $num``` | ```test %reg1, $num``` |
| ```test``` | ```test [mem]``` | ```test %reg1, %reg2``` | ```test %reg1, %reg2``` |
|  |  |  | ```test %reg, [mem]``` |
| *Performs bitwise ```and``` operation between either the ```tos``` and ```num``` or two popped ```tos``` values, changing the flags accordingly* | *Performs bitwise ```and``` operation between the ```num``` (or ```mem```) and ```acc```, changing the flags accordingly* | *Performs bitwise ```and``` operation between the ```reg1``` and ```reg2``` (or ```num```), changing the flags accordingly* | *Performs bitwise ```and``` operation between the ```reg1``` and ```reg2``` (or ```num```, or ```mem```), changing the flags accordingly* |
|||||
| ```jmp $num``` | ```jmp $num``` | ```jmp $num```| ```jmp $num```|
| ```jmp``` | ```jmp``` | ```jmp %reg```| ```jmp %reg```|
| *Jumps to the location at the ```tos``` (or ```num```)* | *Jumps to the location at ```acc``` (or ```num```)* | *Jumps to the location at value of the register ```reg``` (or ```num```)* | *Jumps to the location at value of the register ```reg``` (or ```num```)* |
|||||
| ```je $num``` | ```je $num``` | ```je $num``` | ```je $num``` |
| ```je``` | ```je``` | ```je %reg``` | ```je %reg``` |
| | | | |
| ```jne $num``` | ```jne $num``` | ```jne $num``` | ```jne $num``` |
| ```jne``` | ```jne``` | ```jne %reg``` | ```jne %reg```|
| | | | |
| ```jg $num``` | ```jg $num``` | ```jg $num``` | ```jg $num``` |
| ```jg``` | ```jg```| ```jg %reg```|```jg %reg```|
| | | | |
| ```jge $num``` | ```jge $num``` | ```jge $num``` | ```jge $num``` |
| ```jge``` | ```jge``` | ```jge %reg``` | ```jge %reg``` |
| | | | |
| ```jl $num``` | ```jl $num``` | ```jl $num``` | ```jl $num``` |
| ```jl``` | ```jl``` | ```jl %reg``` | ```jl %reg``` |
| | | | |
| ```jle $num``` | ```jle $num``` | ```jle $num``` | ```jle $num``` |
| ```jle``` | ```jle``` | ```jle %reg``` | ```jle %reg``` |
| *Jumps to the location at the ```tos``` (or ```num```) according to ```jump table```* | *Jumps to the location at ```acc``` (or ```num```) according to ```jump table```* | *Jumps to the location at value of the register ```reg``` (or ```num```) according to the ```jump table```* | *Jumps to the location at value of the register ```reg```(or ```num```) according to the ```jump table```* |
| | | | |
| **I/O Separate Space** |   |   |   |
| ```in $num``` | ```in $num``` | ```in %reg, $num``` | ```in $reg, $num``` |
|  |  |  | ```in [mem], $num```|
| *Transfers data from the device at port ```num``` to ```tos```* | *Transfers data from the device at port ```num``` to ```acc```* | *Transfers data from device at port ```num``` to the register ```reg```* | *Transfers data from device at port ```num``` to the  register at location ```mem```* |
|||||
| ```out $num1, $num2``` | ```out $num1, $num2``` | ```out` $num1, $num2``` | ```out $num1, $num2``` |
| ```out $num``` | ```out $num``` | ```out $num, %reg``` | ```out $num, %reg```|
|  |  |  | ```out $num, [mem]```|
| *Transfers data from ```num2``` (or ```tos```) to the device at port ```num1```* | *Transfers data from ```num2``` (or ```acc```) to the device at port ```num1```* | *Transfers data from ```num2``` (or ```reg```) to the device at port ```num1```* | *Transfers data from ```num2``` (or ```reg```, or from location ```mem```) to the device at port ```num1```* |
|  |  |  |  |
| **SIMD** |   |   |   |
|||| ```add4 %reg1, %reg2``` |
|||| ```sub4 %reg1, %reg2``` |
|||| ```mul4 %reg1, %reg2``` |
|||| ```div4 %reg1, %reg2``` |
| | | | *Computes the needed mathematical operation between two vectors of size 4, with ```reg1``` representing the start of the first vector in memory, and the next popped ```reg2``` representing the start of the second vector in memory. The result is saved in the ```reg1``` memory location* |

- - -

### Jump table
| Instruction name | Assembly instruction | Flags checked |
|-------|----|-----|
| equal | JE | ```zf``` |
| not equal | JNE | ! ```zf``` |
| unsigned below | JL | ```cf``` |
| unsigned below or equal | JLE | ```cf``` or ```zf``` |
| unsigned above or equal | JGE | ! ```cf``` |
| unsigned above | JG | !```cf``` and ! ```zf``` |
| signed less than | JL | ```sf``` != ```of``` |
| signed less or equal | JLE | (```sf``` != ```of```) or ```zf``` |
| signed greater or equal | JGE | ```sf```==```of``` |
| signed greater than | JG | (```sf```==```of```) and ! ```zf``` |
