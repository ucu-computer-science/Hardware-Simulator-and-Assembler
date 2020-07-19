#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0

import logging
from bitarray import bitarray

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
    return operands[2]._state


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
    operands[0]._state = bitarray("0"*8) + operands[2]


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
    operands[0]._state = operands[2]


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

    :param operands: list of operands
    :return: NoneType
    """
    reg1 = int(operands[2].to01(), 2)
    reg2 = int(operands[3].to01(), 2)
    result = reg1 + reg2

    operands[0]._state = bitarray(str(bin(result))[2:])


def sub(operands):
    """
    Performs subtraction of two registers, saving the result in the third one

    Zero operand is a the first register object, for writing information into it
    First one is the value of that register
    Second one is the value of the second register (first operand in subtraction)
    Third one is the value of the third register (second operand in subtraction)

    :param operands: list of operands
    :return: NoneType
    """
    reg1 = int(operands[2].to01(), 2)
    reg2 = int(operands[3].to01(), 2)
    result = reg1 - reg2

    operands[0]._state = bitarray(str(bin(result))[2:])

def mul(operands):
    """
    Performs multiplication of two registers, saving the result in the third one

    Zero operand is a the first register object, for writing information into it
    First one is the value of that register
    Second one is the value of the second register (first operand in multiplication)
    Third one is the value of the third register (second operand in multiplication)

    :param operands: list of operands
    :return: NoneType
    """
    operands[0]._state = bin(int(operands[1]._state) * int(operands[2]._state))


def div(operands):
    """
    Performs division of two registers, saving the result in the third one

    Zero operand is a the first register object, for writing information into it
    First one is the value of that register
    Second one is the value of the second register (first operand in division)
    Third one is the value of the third register (second operand in division)

    :param operands: list of operands
    :return: NoneType
    """
    operands[0]._state = bin(int(operands[1]._state) / int(operands[2]._state))


# def and(operands):
#     pass
#
#
# def or(operands):
#     pass
#
#
# def xor(operands):
#     pass
#
#
# def not(operands):
#     pass
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


functions_dictionary = {"load": load, "mov_low1": mov_low,
                        "mov_low2": mov_low, "mov_high1": mov_high,
                        "mov_high2": mov_high, "mov": mov,
                        "push": push, "pop": pop, "add": add,
                        "sub": sub, "mul": push, "div": div}
