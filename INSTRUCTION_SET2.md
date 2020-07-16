# Instruction Set:

* % –– register (```%reg```)
* [] –– memory location (```[mem]```)
* $ –– constant value (```$42```)

- - -

* Stack architecture uses 6 bits for 30 instructions
    * ```|0|x|x|x|x|x| represents opcode instruction without immediate constants afterwards```
    * ```|1|x|x|x|x|x| represents opcode instruction with immediate constants afterwards```
    * Registers are encoded in 3 bits:
        * Flag register with least significant bits representing flags -
        ```CF```, ```ZF```, ```OF```, ```SF```
        * ```SP```- stack pointer
        * ```IP``` - instruction pointer (can't be directly affected with arithmetical instructions)
        * ```TOS``` – top of the stack register

- - -

* Accumulator architecture uses 8 bits for instructions
    * Registers are encoded in 3 bits:
        * Flag register with least significant bits representing flags -
        ```CF```, ```ZF```, ```OF```, ```SF```
        * ```SP```- stack pointer
        * ```IP``` - instruction pointer (can't be directly affected with arithmetical instructions)
        * ```IR``` - index register (used for addressing the memory)
        * ```ACC``` – accumulator register

- - -

* Register RISC architecture uses 16-bit instructions with first 6 bits for opcode
    * Registers are encoded in 3 bits:
        * Flag register with least significant bits representing flags -
          ```CF```, ```ZF```, ```OF```, ```SF```
        * ```R01, R02, R03, R04 (BP alias)``` with L and H bytes each
        * ```SP```- stack pointer
        * ```IP``` - instruction pointer (can't be directly affected with arithmetical instructions)
        * ```LR``` - link register (for storing the address of the caller)

- - -

* Register CISC architecture uses 1-6 bytes for instructions: ```mov [R01 + off16], imm16```
    * Registers are encoded in 3 bits:
        * Flag register with least significant bits representing flags -
          ```CF```, ```ZF```, ```OF```, ```SF```
        * ```R01, R02, R03, R04 (BP alias)``` with L and H bytes each
        * ```SP```- stack pointer
        * ```IP``` - instruction pointer (can't be directly affected with arithmetical instructions)

- - -

Using Intel-style instructions with results of computations
being saved into the first operand:

```operation destination, <----- source ```

- - -

## Instructions for each architecture

| RISC STACK | RISC ACCUMULATOR | RISC REGISTER | CISC REGISTER |
|------------|------------------|---------------|---------------|
| **Registers** ||||
| ```TOS``` | ```ACC``` | ```R00, R00H, R00L```; ```R01, R01H, R01L```; ```R02, R02H, R02L```; ```R03, R03H, R03L``` | ```R00, R00H, R00L```; ```R01, R01H, R01L```; ```R02, R02H, R02L```; ```R03, R03H, R03L``` |
| | | | |
| **Memory** |   |   |   |
| ```load [mem]``` | ```load``` (Loads the memory cell ```IR``` is pointing to)| ```load %reg, [mem]``` | ```load %reg, [mem]```|
| | ```load %IR``` | | |
|||||
| ```store [mem]``` | ```store``` (Stores in the memory cell ```IR``` is pointing to) | ```store [mem], %reg``` | ```store [mem], %reg``` |
| | ```store %LR``` | | |
| ```swap``` ||||
|||||
| ```dup``` ||||
|||||
| ```dup2``` ||||
|||||
| ```mov $num``` | ```mov $num``` | ```mov %reg, $num``` | ```mov %reg, $num``` |
| | | ```mov %reg1, %reg2``` | ```mov %reg1, %reg2``` |
|||||
| ```push``` | ```push``` | ```push %reg``` | ```push %reg``` |
|  |  | ```push %LR``` (pushes the address of the next instruction into the register) | |
|||||
| ```pop``` | ```pop``` | ```pop %reg``` | ```pop %reg``` |
|  |  | ```pop %LR``` (pops the address of the next instruction from the register)|  |
|||||
| | | | ```enter $num``` |
|||||
| | | | ```leave``` |
| | | | |
| **Arithmetic** |   |   |   |
| ```add``` | ```add [mem]``` | ```add %reg1, %reg2``` | ```add %reg, [mem]``` |
| | ```add %acc```| | ```add [mem1], [mem2]``` |
|||||
| ```sub``` | ```sub [mem]``` | ```sub %reg1, %reg2``` | ```sub %reg, [mem]``` |
|  | ```sub %acc``` |  | ```sub [mem1], [mem2]``` |
|||||
| | | | ```inc %reg``` |
| | | | ```inc [mem]``` |
|||||
| | | | ```dec %reg``` |
| | | | ```dec [mem]``` |
|||||
| ```mul``` | ```mul [mem]``` | ```mul %reg1, %reg2``` | ```mul %reg1, %reg2``` |
| | | | ```mul %reg, [mem]```|
| | | | ```mul %reg, $num```|
|||||
| ```div``` | ```div [mem]``` | ```div %reg1, %reg2``` | ```div %reg1, %reg2``` |
|  |  |  | ```div %reg, [mem]``` |
| | | | ```div %reg, $num```|
| | | | |
| **Logical** |   |   |   |
| ```and``` | ```and [mem]``` | ```and %reg1, %reg2``` | ```and %reg1, %reg2``` |
|  |  |  | ```and %reg, [mem]``` |
|||||
| ```or``` | ```or [mem]``` | ```or %reg1, %reg2``` | ```or %reg1, %reg2``` |
| | | | ```or %reg, [mem]``` |
|||||
| ```xor``` | ```xor [mem]``` | ```xor %reg1, %reg2``` | ```xor %reg1, %reg2``` |
| |  |  | ```xor %reg, [mem]``` |
|||||
| ```not``` | ```not``` | ```not %reg1``` | ```not %reg1``` |
| | | | ```not [mem]``` |
| | | | |
| **Shifts** | | | |
| ```lsh $num``` | ```lsh $num``` | ```lsh %reg, $num``` | ```lsh %reg, $num``` |
|  |  |  | ```lsh [mem], $num``` |
|||||
| ```rsh $num``` | ```rsh $num``` | ```rsh %reg, $num``` | ```rsh %reg, $num```|
|  |  |  | ```rsh [mem], $num```|
| | | | |
| **Flow control** |   |   |   |
| ```call label``` | ```call label``` | ```call label``` | ```call label``` |
| ```call $num``` | ```call $num``` | ```call $num``` | ```call $num``` |
| ```call``` | ```call``` | ```call %reg``` | ```call %reg``` |
|||||
| ```ret``` | ```ret``` | ```ret``` | ```ret``` |
|||||
| **Compares** ||||
| ```cmpe (compare equals)``` | ```cmp [mem]``` | ```cmp %reg1, %reg2``` | ```cmp %reg1, %reg2``` |
| ```cmpb (compare bigger)``` | ```cmp $num``` | ```cmp %reg, $num``` | ```cmp %reg, $num``` |
| *Pushes 0/1 on top of the stack if False/True* |  |  | ```cmp %reg, [mem]``` |
|||||
| ```test``` | ```test [mem]``` | ```test %reg1, %reg2``` | ```test %reg1, %reg2``` |
|  |  |  | ```test %reg, [mem]``` |
|||||
| **Jumps** ||||
| ```jmp $num``` | ```jmp $num``` | ```jmp $num```| ```jmp $num```|
| ```jmp``` | ```jmp``` | ```jmp %reg```| ```jmp %reg```|
|||||
| | ```je $num``` | ```je $num``` | ```je $num``` |
| | ```je``` | ```je %reg``` | ```je %reg``` |
| | | | |
| | ```jne $num``` | ```jne $num``` | ```jne $num``` |
| | ```jne``` | ```jne %reg``` | ```jne %reg```|
| | | | |
| | ```jg $num``` | ```jg $num``` | ```jg $num``` |
| | ```jg```| ```jg %reg```|```jg %reg```|
| | | | |
| | ```jge $num``` | ```jge $num``` | ```jge $num``` |
| | ```jge``` | ```jge %reg``` | ```jge %reg``` |
| | | | |
| | ```jl $num``` | ```jl $num``` | ```jl $num``` |
| | ```jl``` | ```jl %reg``` | ```jl %reg``` |
| | | | |
| | ```jle $num``` | ```jle $num``` | ```jle $num``` |
| | ```jle``` | ```jle %reg``` | ```jle %reg``` |
| | | | |
| **I/O Separate Space** |   |   |   |
| ```in $num``` | ```in $num``` | ```in %reg, $num``` | ```in $reg, $num``` |
|  |  |  | ```in [mem], $num```|
|||||
| ```out $num1, $num2``` | ```out $num1, $num2``` | ```out` $num1, $num2``` | ```out $num1, $num2``` |
| ```out $num``` | ```out $num``` | ```out $num, %reg``` | ```out $num, %reg```|
|  |  |  | ```out $num, [mem]```|
|  |  |  |  |
| **SIMD** |   |   |   |
|||| ```add4 %reg1, %reg2``` |
|||| ```sub4 %reg1, %reg2``` |
|||| ```mul4 %reg1, %reg2``` |
|||| ```div4 %reg1, %reg2``` |

- - -

### Jump tables considered harmful:
| Instruction name | Assembly instruction | Flags checked |
|-------|----|-----|
| equal | ```je``` | ```ZF``` |
| not equal | ```jne``` | ! ```ZF``` |
| unsigned below | ```jl``` | ```CF``` |
| unsigned below or equal | ```jle``` | ```CF``` or ```ZF``` |
| unsigned above or equal | ```jge``` | ! ```CF``` |
| unsigned above | ```jg``` | !```CF``` and ! ```ZF``` |
| signed less than | ```jl``` | ```SF``` != ```OF``` |
| signed less or equal | ```jle``` | (```SF``` != ```OF```) or ```ZF``` |
| signed greater or equal | ```jge``` | ```SF```==```OF``` |
| signed greater than | ```jg``` | (```SF```==```OF```) and ! ```ZF``` |
