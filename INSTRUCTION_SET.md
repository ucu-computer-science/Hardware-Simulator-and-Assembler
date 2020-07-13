# Instruction Set:

* % –– register (```%reg```)
* [] –– memory location (```[mem]```)
* $ –– constant value (```$42```)

Using Intel-style instructions with results of computations
being saved into the first operand:

```operation destination, <----- source ```

*We are not using direct memory access unless we have to (like in accumulator architecture).
This emphasizes the complexity of CISC instructions and eases the actual programming*

| RISC STACK | RISC ACCUMULATOR | RISC REGISTER | CISC REGISTER |
|------------|------------------|---------------|---------------|
| **Registers** |    |   |               |
| | | | |
| **Memory** |   |   |   |
| ```load [mem]``` | ```load [mem]``` | ```load %reg, [mem]``` | ```load %reg, [mem]``` |
| *Loads word from memory at location ```mem``` and pushes into the register on top of the stack* | *Loads word from memory at location ```mem``` into an ```acc``` register* | *Loads word from memory at location ```mem``` into register ```reg```* |  *Loads word from memory at location ```mem``` into register ```reg```* |
| ```store [mem]``` | ```store [mem]``` | ```store [mem], %reg``` | ```store [mem], %reg``` |
| *Copies word from top of the stack and stores it in the memory at location ```mem```* | *Copies word from the ```acc``` register and stores it in the memory at location ```mem```* | *Copies word from the register ```reg``` and stores it in memory  at location ```mem```* | *Copies word from the register ```reg``` and stores it in memory  at location ```mem```* |
| | | | |
| **Arithmetic** |   |   |   |
| ```add``` | ```add [mem]``` | ```add %reg1, %reg2``` | ```add %reg, [mem]``` |
| | ```add %acc```| | ```add [mem1], [mem2]``` |
| *Pops two items from top of the stack, adds their values, pushing the result into the register on top of the stack* | *Add items from the ```acc``` register and memory location ```mem``` (or ```acc``` register), pushing the result into ```acc```* | *Adds items at register ```reg``` and memory location ```mem```, saving the result at ```reg```* | *Adds items at register ```reg``` (or memory location ```mem1```) and memory location ```mem``` (or memory location ```mem2```), saving the result at ```reg``` (or memory location ```mem1```)* |
| ```sub``` | ```sub [mem]``` | ```sub %reg1, %reg2``` | ```sub %reg, [mem]``` |
|  | ```sub %acc``` |  | ```sub [mem1], [mem2]``` |
| *Pops two items from top of the stack, subtracting the second one from the first, and pushes the result into the register on top of the stack* | *Subtracts value stored at location ```mem``` (or register ```acc```) from value stored in ```acc``` register, saving the result in the ```acc``` register* | *Subtracts value at the memory location ```mem``` from the register ```reg```, saving the result in the register ```reg```* | *Subtracts value at the memory location ```mem``` (or at memory location ```mem1```) from the register ```reg``` (or from memory location ```mem1```), saving it in the register ```reg``` (or at the memmory location ```mem1```)* |
| ```inc``` | ```inc [mem]``` | ```inc %reg``` | ```inc %reg``` |
|  | ```inc %acc``` |  | ```inc [mem]``` |
| *Pops the value from top of the stack, increments it, and pushes on top of the stack*| *Increments value from the register ```acc```, saving it in the register ```acc```* | *Increments value from the register ```reg```, saving the result in the register ```reg```* | *Increments value from the register ```reg``` (or at the location ```mem```), saving the result in the register ```reg``` (or at the location ```mem```)* |
| ```dec``` | ```dec [mem]``` | ```dec %reg``` | ```dec %reg``` |
|  |  |  | ```dec [mem]``` |
| *Pops the value from top of the stack, decrements it, and pushes on top of the stack* | *Decrements value from the register ```acc```, saving it in the register ```acc```* | *Decrements value from the register ```reg```, saving the result in the register ```reg```* | *Decrements value from the register ```reg``` (or at the location ```mem```), saving the result in the register ```reg``` (or at the location ```mem```)* |
| ```mul``` | ```mul [mem]``` | ```mul %reg1, %reg2``` | ```mul %reg1, %reg2``` |
| | | | ```mul %reg, [mem]```|
| *Pops two items from top of the stack, multiplies them, and pushes the result into the register on top of the stack* | *Multiplies value from the location ```mem``` and value from the register ```acc```, saving the result in the register ```acc```* | *Multiplies value from the register ```reg1``` and value from the register ```reg2```, saving the result in the register ```reg1```* | *Multiplies value from the register ```reg1```(from the register ```reg```) and value from the register ```reg2```(at location ```mem```), saving the result in the register ```reg1```(in the register ```reg```)* |
| ```div``` | ```div [mem]``` | ```div %reg1, %reg2``` | ```div %reg1, %reg2``` |
|  |  |  | ```div %reg, [mem]``` |
| *Pops two items from top of the stack, dividing the first one by the second, and pushes the result into the register on top of the stack* | *Divides value from the register ```acc``` by value at the location ```mem```, saving the result in the register ```acc```* | *Divides value from the register ```reg1``` by value from the register ```reg2```, saving the result in the register ```reg1```* | *Divides value from the register ```reg1``` (or the register ```reg```) by value from the register ```reg2```(or at location ```mem```), saving the result in the register ```reg1```(or in the register ```reg```)* |
|  |  |  |  |
| **Logical** |   |   |   |
| ```and``` | ```and [mem]``` | ```and %reg1, %reg2``` | ```and %reg1, %reg2``` |
|  |  |  | ```and %reg, [mem]``` |
| *Computes binary ```and``` between two popped values from the stack, pushes the result on to the top of the stack* | *Computes binary ```and``` between word from the ```acc``` register and ```mem``` location, saving the result into ```acc```* | *Computes binary ```and``` between ```reg1``` and ```reg2``` and saves the result into ```reg1```* | *Computes binary ```and``` between ```reg1``` and ```reg2``` (or ```mem``` location) and saves the result into ```reg1``` (or into ```reg```)* |
| ```or``` | ```or [mem]``` | ```or %reg1 %reg2``` | ```or %reg1 %reg2``` |
| | | | ```or %reg [mem]``` |
| *Computes binary ```or``` between two popped values from the stack, pushes the result on to the top of the stack* | *Computes binary ```or``` between word from the ```acc``` register and ```mem``` location, saving the result into ```acc```* | *Computes binary ```or``` between ```reg1``` and ```reg2``` and saves the result into ```reg1```* | *Computes binary ```or``` between ```reg1``` and ```reg2``` (or ```mem``` location) and saves the result into ```reg1``` (or into ```reg```)* |
| ```xor``` | ```xor [mem]``` | ```xor %reg1 %reg2``` | ```xor %reg1 %reg2``` |
| |  |  | ```xor %reg [mem]``` |
| *Computes binary ```xor``` between two popped values from the stack, pushes the result on to the top of the stack* | *Computes binary ```xor``` between word from the ```acc``` register and ```mem``` location, saving the result into ```acc```* | *Computes binary ```xor``` between ```reg1``` and ```reg2``` and saves the result into ```reg1```* | *Computes binary ```xor``` between ```reg1``` and ```reg2``` (or ```mem``` location) and saves the result into ```reg1``` (or into ```reg```)* |
| | | | |
| **Shifts** | | | |
| ```lsh $num``` | ```lsh $num``` | ```lsh %reg $num``` | ```lsh %reg $num``` |
|  |  |  | ```lsh [mem] $num``` |
| *Pops value from the top of the stack, shifts it by ```num``` to the left, and pushes the result into the register on top of the stack* | *Shifts the value from register ```acc``` by ```num``` to the left, saving the result in the register ```acc```* | *Shifts the value from register ```reg``` by ```num``` to the left, saving the result in the register ```reg```* | *Shifts the value from register ```reg``` (or at location ```mem```) by ```num``` to the left, saving the result in the register ```reg```(or at location ```mem```)* |
| ```rsh $num``` | ```rsh $num``` | ```rsh %reg $num``` | ```rsh %reg $num```|
|  |  |  | ```rsh [mem] $num```|
| *Pops value from the top of the stack, shifts it by ```num``` to the right, and pushes the result into the register on top of the stack* | *Shifts the value from register ```acc``` by ```num``` to the right, saving the result in the register ```acc```* | *Shifts the value from register ```reg``` by ```num``` to the right, saving the result in the register ```reg```* | *Shifts the value from register ```reg``` (or at location ```mem```) by ```num``` to the right, saving the result in the register ```reg``` (or at location ```mem```)* |
| | | | |
| **Flow control** |   |   |   |
| ```cmp``` | ```cmp [mem]``` | ```cmp %reg1 %reg2``` | ```cmp %reg1 %reg2``` |
|  |  |  | ```cmp %reg [mem]``` |
| ** | ** | ** | ** |
| ```jmp $num``` | ```jmp $num``` | ```jmp $num```| ```jmp $num```|
| ```jmp``` | ```jmp``` | ```jmp %reg```| ```jmp %reg```|
| ** | ** | ** | ** |
| | | | |
| **I/O** |   |   |   |
| ```in $num``` | ```in $num``` | ```in $num``` | ```in $num``` |
| ```in``` | ```in``` | ```in %reg``` | ```in %reg```|
|  |  |  | ```in [mem]```|
| ** | ** | ** | ** |
| ```out $num``` | ```out $num``` | ```out $num``` | ```out $num``` |
| ```out``` | ```out``` | ```out %reg``` | ```out %reg```|
|  |  |  | ```out [mem]```|
| ** | ** | ** | ** |
