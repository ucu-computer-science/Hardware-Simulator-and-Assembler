#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0

import logging
from bitarray import bitarray

logging.basicConfig(filename="log.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger('funclogger')


def load(operands):
    operands[0]._state = operands[1]


def store(operands):
    operands[0] = operands[1]._state


def mov_low(operands):
    operands[0]._state = bitarray("0"*8) + operands[2]


def mov_high(operands):
    operands[0]._state[:8] = operands[2]


def mov(operands):
    operands[0]._state = operands[2]


def push(operands):
    pass


def pop(operands):
    pass


def add(operands):
    result = bitarray("0"*16)
    flag = 0

    for i in range(len(operands[2])):
        if flag:
            result[i] = "1"

        addition = int(operands[2][len(operands[2])-i-1]) + int(operands[3][len(operands[3])-i-1])
        if addition == 2:
            flag = 1

        else:
            if int(result[i]) + addition == 2:
                flag = 1
            elif int(result[i]) + addition == 1:
                result[i] = "1"
                flag = 0
            else:
                flag = 0

    operands[0]._state = result[::-1]


def sub(operands):
    operands[0]._state = bin(int(operands[1]._state) - int(operands[2]._state))


def mul(operands):
    operands[0]._state = bin(int(operands[1]._state) * int(operands[2]._state))


def div(operands):
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
