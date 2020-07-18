# Instruction Set:

* % –– register (```%reg```)
* [] –– memory location (```[mem]```)
* $ –– immediate value, constant (```$42```)


- - -

Stack architecture uses 6 bits for 37 instructions
* ```|0|x|x|x|x|x| represents opcode instruction without immediate constants afterwards```
* ```|1|x|x|x|x|x| represents opcode instruction with immediate constants afterwards```
* Registers:
    * ```FR``` Flag register with least significant bits representing flags -
    ```CF```, ```ZF```, ```OF```, ```SF```
    * ```SP```- stack pointer
    * ```IP``` - instruction pointer (can't be directly affected with arithmetical instructions)
    * ```TOS``` – top of the stack register

Instructions look like:

```| 1 bit immediate sign | 5-bit opcode |```

And immediate constants contain two 6-bit bytes:

```| 6-bit immediate high byte| 6-bit immediate low byte |```

- - -

Accumulator architecture uses 8 bits for 49 instructions
* Registers:
    * ```FR``` Flag register with least significant bits representing flags -
    ```CF```, ```ZF```, ```OF```, ```SF```
    * ```SP```- stack pointer
    * ```IP``` - instruction pointer (can't be directly affected with arithmetical instructions)
    * ```IR``` - index register (used for addressing the memory, some instructions implicitly use ```%acc``` or ```[%IR]```)
    * ```ACC``` – accumulator register

Instructions look like:

```| 1 bit immediate sign | 7-bit opcode |```

And immediate constants contain two 8-bit bytes:

```| 8-bit immediate high byte | 8-bit immediate low byte |```

- - -

Register RISC architecture uses 16-bit instructions with first 6 bits for opcode (40 instructions)
* 8 Registers are encoded in 3 bits:
    * ```FR``` Flag register with least significant bits representing flags -
      ```CF```, ```ZF```, ```OF```, ```SF``` (not a general-purpose register)
    * ```R00, R01, R02, R03 (BP alias)``` with L and H bytes each
    * ```SP```- stack pointer
    * ```IP``` - instruction pointer (can't be directly affected with arithmetical instructions)
    * ```LR``` - link register (stores call return address)

Instructions look like:

* for three registers (dest = src1, src2):
    ```| 6-bit opcode | 3-bit register | 3-bit register | 3-bit register | 1 empty bit |```

* for a register and immediate constant
    ```| 6-bit opcode | 3-bit register | 7-bit constant |```

* for immediate constant
    ```| 6-bit opcode | 10-bit constant |```


And load immediate constants instructions look like:

```| 5-bit opcode for high/low load | 3-bit register | 8-bit immediate constant low/high byte |```

- - -

Register CISC architecture uses 1-6 bytes for instructions:
* 7 Registers are encoded in 3 bits:
    * ```FR``` Flag register with least significant bits representing flags -
      ```CF```, ```ZF```, ```OF```, ```SF``` (not a general-purpose register)
    * ```R00, R01, R02, R03``` with L and H bytes each
    * ```BP``` - base pointer
    * ```SP```- stack pointer
    * ```IP``` - instruction pointer (can't be directly affected with arithmetical instructions)

Instructions look like this:

* ```| 3-bit style specifier | 5-bit opcode | ```
* ```| 3-bit style specifier | 5-bit opcode | 3-bit register |```
* ```| 3-bit style specifier | 5-bit opcode | 16-bit constant |```
* ```| 3-bit style specifier | 5-bit opcode | 3-bit register | 3-bit register |```
* ```| 3-bit style specifier | 5-bit opcode | 3-bit register | 16-bit constant |```

Offset instruction:
* ```| 3-bit style specifier | 5-bit opcode | 3-bit register | 16-bit constant |```
* ```| 3-bit style specifier | 5-bit opcode | 3-bit register | 16-bit constant | 3-bit register |```
* ```| 3-bit style specifier | 5-bit opcode | 3-bit register | 3-bit register | 16-bit constant |```

- - -

Using Intel-style instructions with results of computations
being saved into the first operand:

``` operation destination, <----- source ```

- - -

## Instructions for each architecture

| RISC STACK | RISC ACCUMULATOR | RISC REGISTER | CISC REGISTER |
|------------|------------------|---------------|---------------|
| **Registers** ||||
| ```TOS```; ```CF```; ```SP```; ```IP```  | ```ACC```; ```IR```; ```FR```; ```SP```; ```IP``` | ```R00: R00H, R00L```; ```R01: R01H, R01L```; ```R02: R02H, R02L```; ```R03: R03H, R03L```; ```LR```; ```FR```; ```SP```; ```IP```   | ```R00: R00H, R00L```; ```R01: R01H, R01L```; ```R02: R02H, R02L```; ```R03: R03H, R03L```; ```FR```; ```BP``; ```SP```; ```IP```  |
| | | | |
| **Memory** |   |   |   |
| ```load``` | ```load``` (Loads the memory cell ```IR``` is pointing to)| ```load %reg1, [%reg2]``` | |
| ```load %FR ``` | ```load %FR``` | | |
| ```load [imm]``` | ```load %IR``` | | |
|  | ```load [imm]``` | |
|||||
| ```store``` | ```store``` (Stores in the memory cell ```IR``` is pointing to) | ```store [%reg1], %reg2``` | |
| ```store [imm] ``` | ```store [imm]``` | | |
| ```store %FR``` | ```store %IR``` | | |
|| ```store %FR``` |||
|||||
| ```swap``` ||||
|||||
| ```dup``` ||||
|||||
| ```dup2``` ||||
|||||
| ```mov $imm``` | ```mov $imm``` | ```mov %reg, $imm``` | ```mov %reg, $imm``` |
| | | ```mov %reg1, %reg2``` | ```mov %reg1, %reg2``` |
||||```mov %reg1, [%reg2]```|
||||```mov %reg1, [%reg2+$off]```|
||||```mov [%reg1], %reg2```|
||||```mov [%reg1], $imm```|
||||```mov [%reg1+$off], %reg2```|
||||```mov [%reg1+$off], $imm```|
|||||
| ```push``` | ```push``` | ```push %reg``` | ```push %reg``` |
|  | ```push %IR``` (pushes the address of the next instruction into the register) | | |
| ```pushf``` | ```pushf``` | | |
|  |  | | ```push $imm``` |
|||||
| ```pop``` | ```pop``` | ```pop %reg``` | ```pop %reg``` |
|  | ```pop %IR``` (pops the address of the next instruction from the register) | |  |
| ```popf``` | ```popf``` | | |
|||||
| | | | ```enter $imm``` |
|||||
| | | | ```leave``` |
| | | | |
| **Arithmetic** |   |   |   |
| ```add``` | ```add``` | ```add %reg1, %reg2, %reg3``` | ```add %reg1, [%reg2]``` |
| | | | ```add %reg1, %reg2``` |
|||| ```add %reg1, [%reg2+$off]```|
|||| ```add [%reg1], %reg2```|
|||||
| ```sub``` | ```sub``` | ```sub %reg1, %reg2, %reg3``` | ```sub %reg1, [%reg2]``` |
| | | | ```sub %reg1, %reg2``` |
|||| ```sub %reg1, [%reg2+$off]```|
|||| ```sub [%reg1], %reg2```|
|||||
| | ```inc %IR``` | | ```inc %reg``` |
| | | | ```inc [%reg]``` |
| | | | ```inc [%reg+$off]``` |
|||||
| | ```dec %IR``` | | ```dec %reg``` |
| | | | ```dec [%reg]``` |
| | | | ```dec [%reg+$off]``` |
|||||
| ```mul``` | ```mul``` | ```mul %reg1, %reg2, %reg3``` | ```mul %reg1, %reg2``` |
| | | | ```mul %reg1, [%reg2]```|
| | | | ```mul [%reg1], %reg2```|
|  |  |  | ```div [%reg1], %reg2``` |
| | | | ```mul %reg, $imm```|
|||| ```mul %reg1, [%reg2+$off]```|
|||||
| ```div``` | ```div``` | ```div %reg1, %reg2, %reg3``` | ```div %reg1, %reg2``` |
|  |  |  | ```div %reg1, [%reg2]``` |
|  |  |  | ```div [%reg1], %reg2``` |
| | | | ```div %reg, $imm```|
|||| ```div %reg1, [%reg2+$off]```|
| | | | |
| **Logical** |   |   |   |
| ```and``` | ```and``` | ```and %reg1, %reg2, %reg3``` | ```and %reg1, %reg2``` |
|  |  |  | ```and %reg1, [%reg2]``` |
|  |  |  | ```and [%reg1], %reg2``` |
|||||
| ```or``` | ```or``` | ```or %reg1, %reg2, %reg3``` | ```or %reg1, %reg2``` |
| | | | ```or %reg1, [%reg2]``` |
| | | | ```or [%reg1], %reg2``` |
|||||
| ```xor``` | ```xor``` | ```xor %reg1, %reg2, %reg3``` | ```xor %reg1, %reg2``` |
| |  |  | ```xor %reg1, [%reg2]``` |
| |  |  | ```xor [%reg1], %reg2``` |
|||||
| ```not``` | ```not``` (only with ```acc```)| ```not %reg1, %reg2``` | ```not %reg1``` |
| | | | ```not [%reg]``` |
| | | | |
| **Shifts** | | | |
| ```lsh $imm``` | ```lsh $imm``` | ```lsh %reg1, %reg2 , %reg3``` | ```lsh %reg, $imm``` |
|  |  |  | ```lsh [%reg], $imm``` |
|  |  |  | ```lsh [%reg+$off], $imm``` |
|||||
| ```rsh $imm``` | ```rsh $imm``` | ```rsh %reg1, %reg2, %reg3``` | ```rsh %reg, $imm```|
|  |  |  | ```rsh [%reg], $imm```|
|  |  |  | ```rsh [%reg+$off], $imm``` |
| | | | |
| **Flow control** |   |   |   |
| ```call label``` | ```call label``` | ```call label``` | ```call label``` |
| ```call $imm``` | ```call $imm``` | ```call [$imm]``` | ```call [imm]``` |
| ```call``` | ```call``` | ```call [%reg]``` | ```call [%reg]``` |
| | | | ```call [%reg+$off]``` |
|||||
| ```ret``` | ```ret``` | ```ret``` | ```ret``` |
|||||
| **Compares** ||||
| ```cmpe (compare equals)``` | ```cmp``` | ```cmp %reg1, %reg2``` | ```cmp %reg1, %reg2``` |
| ```cmpe $imm``` ||| ```cmp %reg, $imm``` |
| ```cmpb (compare bigger)``` | ```cmp $imm``` | ```cmp %reg, $imm``` | ```cmp %reg1, [%reg2]``` |
| ```cmpb $imm``` ||| ```cmp %reg1, [%reg2+$off]``` |
| *Pushes 0*16/1*16 words on top of the stack if False/True* |  |  |  |
|||||
| ```test``` | ```test``` | ```test %reg1, %reg2``` | ```test %reg1, %reg2``` |
| ```test $imm``` | ```test $imm``` |  | ```test %reg1, [%reg2]``` |
| | | | ```test %reg1, [%reg2+$off]``` |
| | |  | ```test [%reg1], %reg2``` |
|||||
| **Jumps** ||||
| ```jmp [$off]``` | ```jmp [$off]``` | ```jmp [$off]```| ```jmp [$off]```|
| *Jumps to the IP+off address in memory* | *Jumps to the IP+off address in memory* | *Jumps to the IP+off address in memory* | *Jumps to the IP+off address in memory* |
| ```jmp``` | ```jmp``` | ```jmp [%reg]```| ```jmp [%reg]```|
| *Jumps to the ```tos``` address in memory* | *Jumps to the ```acc``` address in memory* | *Jumps to the ```reg``` address in memory* | *Jumps to the ```reg``` address in memory* |
| | | | ```jmp [%reg+$off]```|
| | | | *Jumps to the ```reg + off``` address in memory* |
|||||
| | ```je [$off]``` | ```je [$off]``` | ```je [$off]``` |
| | | | |
| | ```jne [$off]``` | ```jne [$off]``` | ```jne [$off]``` |
| | | | |
| | ```jg [$off]``` | ```jg [$off]``` | ```jg [$off]``` |
| | | | |
| | ```jge [$off]``` | ```jge [$off]``` | ```jge [$off]``` |
| | | | |
| | ```jl [$off]``` | ```jl [$off]``` | ```jl [$off]``` |
| | | | |
| | ```jle [$off]``` | ```jle [$off]``` | ```jle [$off]``` |
| | | | |
| **I/O Separate Space** |   |   |   |
| ```in $port``` | ```in $port``` | ```in %reg, $port``` | ```in $reg, $port``` |
|  |  |  | ```in [%reg], $port```|
|  |  |  | ```in [%reg+$off], $port```|
|||||
| ```out $port, $imm``` | ```out $port, $imm``` | ```out $port, $imm``` | ```out $port, $imm``` |
| ```out $port``` | ```out $port``` | ```out $port, %reg``` | ```out $port, %reg```|
|  |  |  | ```out $port, [%reg]```|
|  |  |  | ```out $port, [%reg+$off]```|
|  |  |  |  |
| **SIMD** |   |   |   |
| | | | ```load4 [%reg]``` |
| | | | ```store4 [%reg]``` |
| | | | ```add4 [%reg1], [%reg2]``` |
| | | | ```sub4 [%reg1], [%reg2]``` |
| | | | ```mul4 [%reg1], [%reg2]``` |
| | | | ```div4 [%reg1], [%reg2]``` |
| | | | ```cmp4 [%reg1], [%reg2]``` |
| | | | ```test4 [%reg1], [%reg2]``` |
| | | | *The first register represents the start of the first 4-word vector in memory. The second register represents the start of the second 4-word vector in memory. Values inside the vector are required to go one after another in the memory* |

- - -

### Jump conditions (for register RISC, CISC and accumulator):
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
