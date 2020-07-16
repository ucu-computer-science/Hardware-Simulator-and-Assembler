# Instruction Set:

* % –– register (```%reg```)
* [] –– memory location (```[mem]```)
* $ –– constant value (```$42```)


- - -

* Stack architecture uses 6 bits for 34 instructions
    * ```|0|x|x|x|x|x| represents opcode instruction without immediate constants afterwards```
    * ```|1|x|x|x|x|x| represents opcode instruction with immediate constants afterwards```
    * Registers:
        * ```CF``` - carry flag register
        * ```SP```- stack pointer
        * ```IP``` - instruction pointer (can't be directly affected with arithmetical instructions)
        * ```TOS``` – top of the stack register

Instructions look like:

```| 1 bit immediate sign | 5-bit opcode |```

And immediate constants contain two 6-bit bytes:

```| 6-bit immediate high byte| 6-bit immediate low byte |```

- - -

* Accumulator architecture uses 8 bits for 41 instructions
    * Registers:
        * Flag register with least significant bits representing flags -
        ```CF```, ```ZF```, ```OF```, ```SF```
        * ```SP```- stack pointer
        * ```IP``` - instruction pointer (can't be directly affected with arithmetical instructions)
        * ```IR``` - index register (used for addressing the memory, every instruction implicitly uses ```%acc```, ```[%IR]```)
        * ```ACC``` – accumulator register

Instructions look like:

```| 1 bit immediate sign | 7-bit opcode |```

And immediate constants contain two 8-bit bytes:

```| 8-bit immediate high byte | 8-bit immediate low byte |```

- - -

* Register RISC architecture uses 16-bit instructions with first 6 bits for opcode
    * 8 Registers are encoded in 3 bits:
        * ```FR``` Flag register with least significant bits representing flags -
          ```CF```, ```ZF```, ```OF```, ```SF```
        * ```R01, R02, R03, R04 (BP alias)``` with L and H bytes each
        * ```SP```- stack pointer
        * ```IP``` - instruction pointer (can't be directly affected with arithmetical instructions)
        * ```LR``` - link register (for storing the address of the caller)

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

* Register CISC architecture uses 1-6 bytes for instructions:
    * 7 Registers are encoded in 3 bits:
        * ```FR``` Flag register with least significant bits representing flags -
          ```CF```, ```ZF```, ```OF```, ```SF```
        * ```R01, R02, R03, R04 (BP alias)``` with L and H bytes each
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
| ```TOS``` | ```ACC``` | ```R00, R00H, R00L```; ```R01, R01H, R01L```; ```R02, R02H, R02L```; ```R03, R03H, R03L``` | ```R00, R00H, R00L```; ```R01, R01H, R01L```; ```R02, R02H, R02L```; ```R03, R03H, R03L``` |
| | | | |
| **Memory** |   |   |   |
| ```load``` | ```load``` (Loads the memory cell ```IR``` is pointing to)| ```load %reg1, [%reg2]``` | ```load %reg1, [%reg2]```|
| ```load %FR ``` | ```load %IR``` | | ```loado %reg1, [%reg2+$num]``` |
| ```load [num]``` | ```load %СF``` | | |
|  | ```load [num]``` | |
|||||
| ```store``` | ```store``` (Stores in the memory cell ```IR``` is pointing to) | ```store [%reg1], %reg2``` | ```store [%reg1], %reg2``` |
| ```store [num] ``` | ```store [num]``` | | ```storeo [%reg1+$num], %reg2```|
| ```store %FR``` | ```store %IR``` | | |
|||||
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
|  | ```push %IR``` (pushes the address of the next instruction into the register) | | |
|||||
| ```pop``` | ```pop``` | ```pop %reg``` | ```pop %reg``` |
|  | ```pop %IR``` (pops the address of the next instruction from the register) | |  |
|||||
| | | | ```enter $num``` |
|||||
| | | | ```leave``` |
| | | | |
| **Arithmetic** |   |   |   |
| ```add``` | ```add``` | ```add %reg1, %reg2, %reg3``` | ```add %reg1, [%reg2]``` |
|||| ```addo %reg1, [%reg2+$num]```|
| | | | ```add %reg1, %reg2``` |
|||||
| ```sub``` | ```sub``` | ```sub %reg1, %reg2, %reg3``` | ```sub %reg1, [%reg2]``` |
|||| ```subo %reg1, [%reg2+$num]```|
| | | | ```sub %reg1, %reg2``` |
|||||
| | ```inc %IR``` | | ```inc %reg``` |
| | | | ```inc [%reg]``` |
| | | | ```inc [%reg+$num]``` |
|||||
| | ```dec %IR``` | | ```dec %reg``` |
| | | | ```dec [%reg]``` |
| | | | ```dec [%reg+$num]``` |
|||||
| ```mul``` | ```mul``` | ```mul %reg1, %reg2, %reg3``` | ```mul %reg1, %reg2``` |
| | | | ```mul %reg1, [%reg2]```|
| | | | ```mul %reg, $num```|
|||| ```mulo %reg1, [%reg2+$num]```|
|||||
| ```div``` | ```div``` | ```div %reg1, %reg2, %reg3``` | ```div %reg1, %reg2``` |
|  |  |  | ```div %reg1, [%reg2]``` |
| | | | ```div %reg, $num```|
|||| ```divo %reg1, [%reg2+$num]```|
| | | | |
| **Logical** |   |   |   |
| ```and``` | ```and``` | ```and %reg1, %reg2, %reg3``` | ```and %reg1, %reg2``` |
|  |  |  | ```and %reg1, [%reg2]``` |
|||||
| ```or``` | ```or``` | ```or %reg1, %reg2, %reg3``` | ```or %reg1, %reg2``` |
| | | | ```or %reg1, [%reg2]``` |
|||||
| ```xor``` | ```xor``` | ```xor %reg1, %reg2, %reg3``` | ```xor %reg1, %reg2``` |
| |  |  | ```xor %reg1, [%reg2]``` |
|||||
| ```not``` | ```not``` (only with ```acc```)| ```not %reg1, %reg2``` | ```not %reg1``` |
| | | | ```not [%reg]``` |
| | | | |
| **Shifts** | | | |
| ```lsh $num``` | ```lsh $num``` | ```lsh %reg1, %reg2 , %reg3``` | ```lsh %reg, $num``` |
|  |  |  | ```lsh [%reg], $num``` |
|  |  |  | ```lsh [%reg+$num1], $num2``` |
|||||
| ```rsh $num``` | ```rsh $num``` | ```rsh %reg1, %reg2, %reg3``` | ```rsh %reg, $num```|
|  |  |  | ```rsh [%reg], $num```|
|  |  |  | ```rsh [%reg+$num1], $num2``` |
| | | | |
| **Flow control** |   |   |   |
| ```call label``` | ```call label``` | ```call label``` | ```call label``` |
| ```call $num``` | ```call $num``` | ```call $num``` | ```call $num``` |
| ```call``` | ```call``` | ```call %reg``` | ```call %reg``` |
|||||
| ```ret``` | ```ret``` | ```ret``` | ```ret``` |
|||||
| **Compares** ||||
| ```cmpe (compare equals)``` | ```cmp``` | ```cmp %reg1, %reg2``` | ```cmp %reg1, %reg2``` |
| ```cmpe $num``` ||| ```cmp %reg, $num``` |
| ```cmpb (compare bigger)``` | ```cmp $num``` | ```cmp %reg, $num``` | ```cmp %reg1, [%reg2]``` |
| ```cmpb $num``` ||| ```cmp %reg1, [%reg2+$num]``` |
| *Pushes 0/1 on top of the stack if False/True* |  |  |  |
|||||
| ```test``` | ```test``` | ```test %reg1, %reg2``` | ```test %reg1, %reg2``` |
| ```test $num``` | ```test $num``` |  | ```test %reg1, [%reg2]``` |
| | | | ```test %reg1, [%reg2+$num]``` |
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
| | ```jge```| ```jge %reg``` | ```jge %reg``` |
| | | | |
| | ```jl $num``` | ```jl $num``` | ```jl $num``` |
| | ```jl``` | ```jl %reg``` | ```jl %reg``` |
| | | | |
| | ```jle $num``` | ```jle $num``` | ```jle $num``` |
| | ```jle``` | ```jle %reg``` | ```jle %reg``` |
| | | | |
| **I/O Separate Space** |   |   |   |
| ```in $num``` | ```in $num``` | ```in %reg, $num``` | ```in $reg, $num``` |
|  |  |  | ```in [%reg], $num```|
|  |  |  | ```ino [%reg+$num1], $num2```|
|||||
| ```out $num1, $num2``` | ```out $num1, $num2``` | ```out $num1, $num2``` | ```out $num1, $num2``` |
| ```out $num``` | ```out $num``` | ```out $num, %reg``` | ```out $num, %reg```|
|  |  |  | ```out $num, [%reg]```|
|  |  |  | ```outo $num1, [%reg+$num2]```|
|  |  |  |  |
| **SIMD** |   |   |   |
|||| ```load4 %reg``` |
|||| ```store4 %reg``` |
|||| ```add4 %reg1, %reg2``` |
|||| ```sub4 %reg1, %reg2``` |
|||| ```mul4 %reg1, %reg2``` |
|||| ```div4 %reg1, %reg2``` |
|||| ```cmp4 %reg1, %reg2``` |
|||| ```test4 %reg1, %reg2``` |

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
