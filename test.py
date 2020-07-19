import os
import json
from bitarray import bitarray

with open(os.path.join("modules", "registers.json"), "r") as file:
    registers_list = json.load(file)["risc3"]

print(registers_list)

registers = dict()
register_codes = dict()

for register in registers_list:
    temp = (register[0], 1)
    registers[register[0]] = temp
    register_codes[register[2]] = temp

print(registers)
print(register_codes)


def bit_and(operands):
    reg1 = int(operands[2].to01(), 2)
    reg2 = int(operands[3].to01(), 2)
    result = str(bin(reg1 & reg2))[2:]

    if result == "0":
        operands[4]._state[13] = "1"  # Zero flag

    while len(result) != 16:
        result = "0" + result

    return result


def twos_complement(val, bits):
    """
    Works with signed bit numbers
    :param val: int - int value of the bit number
    :param bits: int - length of the bit number
    """
    if (val & (1 << (bits - 1))) != 0:
        val -= (1 << bits)
    return val


binary_string = '1001'  # or whatever... no '0b' prefix
out = twos_complement(int(binary_string, 2), len(binary_string))
print(out)

def from_int_to_signed_binary(int_value, len_int_value):
    max_diff = 2**(len_int_value-1)




print(from_int_to_signed_binary(-7, 4))

def add(operands):
    """
    Performs addition of two registers, saving the result in the third one

    Zero operand is a the first register object, for writing information into it
    First one is the value of that register
    Second one is the value of the second register (first operand in addition)
    Third one is the value of the third register (second operand in addition)
    Forth one os the value of Flag register

    :param operands: list of operands
    :return: NoneType
    """
    reg1 = twos_complement(int(operands[2].to01(), 2), len(operands[2]))
    reg2 = twos_complement(int(operands[3].to01(), 2), len(operands[3]))
    print(reg1, reg2)
    result = bin(twos_complement(reg1 + reg2, len(operands[1])))[2:]
    print(result)

    if len(result) > 16:
        operands[4][12] = "1"  # Carry flag
        result = result[-16:]
    elif len(result) == 16:
        operands[4][14] = "1"  # Overflow flag
    elif result == "0":
        result = "0" * 16
        operands[4][13] = "1"  # Zero flag
    else:
        result = result.rjust(16, "0")

    return result, operands

print(add([1, bitarray("0000000000000001"), bitarray("0111111111111111"), bitarray("0000000000000001"), ["0"]*16]))
