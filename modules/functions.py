#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0

import logging
from bitarray import bitarray

# About Flag register:
# Flags in the register are represented like  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | CF | ZF | OF | SF |

logging.basicConfig(filename="../log.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger('funclogger')


def load(operands):
    """
    Loads value from memory to register
    Zero operand is register (destination)
    First is its vale
    Second is the value to be stored

    :param operands: list of operands
    :return: NoneType
    """
    operands[0]._state = operands[2]


def store(operands):
    """
    Returns value, which later will be stored in the memory by CPU
    Zero operand is register with memory location
    First is its vale
    Second is the value to be stored

    :param operands: list of operands
    :return: bitarray
    """
    return operands[2]


def mov_low(operands):
    """
    Writes immediate constant into the low byte of the register,
    setting high byte to all zeros

    Zero operand is a register object, for writing information into it
    First one is the value of that register
    Second one is the value of the immediate constant

    :param operands: list of operands
    :return: NoneType
    """
    operands[0]._state = bitarray("0" * 8) + operands[2]


def mov_high(operands):
    """
    Writes immediate constant into the high byte of the register,
    does not affect the low byte

    Zero operand is a register object, for writing information into it
    First one is the value of that register
    Second one is the value of the immediate constant

    :param operands: list of operands
    :return: NoneType
    """
    operands[0]._state[:8] = operands[2]


def mov(operands):
    """
    Writes register value into another register

    Zero operand is a register object, for writing information into it
    First one is the value of that register
    Second one is the value of the second register, which will be written
    into the first one

    :param operands: list of operands
    :return: NoneType
    """
    operands[0]._state = bitarray(operands[2].to01())


def push(operands):
    pass


def pop(operands):
    pass


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
    reg1 = int(operands[2].to01(), 2)
    reg2 = int(operands[3].to01(), 2)
    result = str(bin(reg1 + reg2))[2:]

    if len(result) > 16:
        operands[4]._state[12] = "1"  # Carry flag
        result = result[-16:]
    elif len(result) == 16:
        operands[4]._state[14] = "1"  # Overflow flag
    elif result == "0":
        result = "0" * 16
        operands[4]._state[13] = "1"  # Zero flag
    else:
        result = result.rjust(16, "0")

    operands[0]._state = bitarray(result)


def sub(operands):
    """
    Performs subtraction of two registers, saving the result in the third one

    Zero operand is a the first register object, for writing information into it
    First one is the value of that register
    Second one is the value of the second register (first operand in subtraction)
    Third one is the value of the third register (second operand in subtraction)
    Forth one os the value of Flag register

    :param operands: list of operands
    :return: NoneType
    """
    reg1 = int(operands[2].to01(), 2)
    reg2 = int(operands[3].to01(), 2)
    result = str(bin(reg1 - reg2))[2:]

    if len(result) > 16:
        operands[4]._state[12] = "1"  # Carry flag
    elif len(result) == 16:
        operands[4]._state[14] = "1"  # Overflow flag
    elif result == "0":
        result = "0" * 16
        operands[4]._state[13] = "1"  # Zero flag
    else:
        result = result.rjust(16, "0")

    operands[0]._state = bitarray(str(bin(result))[2:])


def mul(operands):
    """
    Performs multiplication of two registers, saving the result in the third one

    Zero operand is a the first register object, for writing information into it
    First one is the value of that register
    Second one is the value of the second register (first operand in multiplication)
    Third one is the value of the third register (second operand in multiplication)
    Forth one os the value of Flag register

    :param operands: list of operands
    :return: NoneType
    """
    reg1 = int(operands[2].to01(), 2)
    reg2 = int(operands[3].to01(), 2)
    result = str(bin(reg1 * reg2))[2:]

    if len(result) > 16:
        operands[4]._state[12] = "1"  # Carry flag
        result = result[-16:]
    elif len(result) == 16:
        operands[4]._state[14] = "1"  # Overflow flag
    elif result == "0":
        result = "0" * 16
        operands[4]._state[13] = "1"  # Zero flag
    else:
        result = result.rjust(16, "0")

    operands[0]._state = bitarray(result)


def div(operands):
    """
    Performs division of two registers, saving the result in the third one

    Zero operand is a the first register object, for writing information into it
    First one is the value of that register
    Second one is the value of the second register (first operand in division)
    Third one is the value of the third register (second operand in division)
    Forth one os the value of Flag register

    :param operands: list of operands
    :return: NoneType
    """
    reg1 = int(operands[2].to01(), 2)
    reg2 = int(operands[3].to01(), 2)
    result = str(bin(reg1 // reg2))[2:]

    if len(result) > 16:
        operands[4]._state[12] = "1"  # Carry flag
        result = result[-16:]
    elif len(result) == 16:
        operands[4]._state[14] = "1"  # Overflow flag
    elif result == "0":
        result = "0" * 16
        operands[4]._state[13] = "1"  # Zero flag
    else:
        result = result.rjust(16, "0")

    operands[0]._state = bitarray(result)


def bit_and(operands):
    reg1 = int(operands[2].to01(), 2)
    reg2 = int(operands[3].to01(), 2)
    result = str(bin(reg1 & reg2))[2:]

    if result == "0":
        operands[4]._state[13] = "1"  # Zero flag

    while len(result) != 16:
        result = "0" + result

    operands[0]._state = bitarray(result)


def bit_or(operands):
    reg1 = int(operands[2].to01(), 2)
    reg2 = int(operands[3].to01(), 2)
    result = str(bin(reg1 | reg2))[2:]

    if result == "0":
        operands[4]._state[13] = "1"  # Zero flag

    while len(result) != 16:
        result = "0" + result

    operands[0]._state = bitarray(result)


def bit_xor(operands):
    reg1 = int(operands[2].to01(), 2)
    reg2 = int(operands[3].to01(), 2)
    result = str(bin(reg1 ^ reg2))[2:]

    if result == "0":
        operands[4]._state[13] = "1"  # Zero flag

    while len(result) != 16:
        result = "0" + result

    operands[0]._state = bitarray(result)


def bit_not(operands):
    result = operands[1].to01()
    result.replace("1", "2")
    result.replace("0", "1")
    result.replace("2", "0")

    if result == "0" * 16:
        operands[4]._state[13] = "1"  # Zero flag

    operands[0]._state = bitarray(result)


#
#
# def lsh(operands):
#     pass
#
#
# def rsh(operands):
#     pass
#
#
# def call1(operands):
#     pass
#
#
# def call2(operands):
#     pass
#
#
# def call3(operands):
#     pass
#
#
# def ret(operands):
#     pass
#
#
# def cmp1(operands):
#     pass
#
#
# def cmp2(operands):
#     pass
#
#
# def test(operands):
#     pass


def twos_complement(val, bits):
    """
    Works with signed bit numbers
    :param val: int - int value of the bit number
    :param bits: int - length of the bit number
    """
    if val < 0:
        val = (1 << bits) + val
    else:
        if (val & (1 << (bits - 1))) != 0:
            val = val - (1 << bits)
    return val


functions_dictionary = {"load": load, "mov_low": mov_low,
                        "mov_high": mov_high, "mov": mov,
                        "push": push, "pop": pop, "add": add,
                        "sub": sub, "mul": push, "div": div,
                        "and": bit_and, "or": bit_or,
                        "xor": bit_xor, "not": bit_not,
                        "store": store}
