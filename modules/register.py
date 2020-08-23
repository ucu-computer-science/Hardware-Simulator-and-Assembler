#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0

from bitarray import bitarray


class Register:
    """
    Register simulator class
    Handles the creation of registers of different
    types and their available options
    """

    def __init__(self, name, general_purpose=False):
        """
        Initializes register object, holding 16 bits,
        specifying its visibility for dev purposes
        :return: NoneType
        """
        self.name = name
        self._state = bitarray('0'*16)
        self.accessibility = general_purpose

    def write_data(self, value):
        """
        Writes the data provided into its state
        :param value: str - binary string representing bits
        """
        if isinstance(value, str):
            self._state = bitarray(value.rjust(16, '0'))
        elif isinstance(value, bitarray):
            self._state = bitarray(value.to01().rjust(16, '0'))

    def get_low(self):
        """
        Returns the low byte if the register is accessible
        :return: last 8 bits of the register
        """
        if self.accessibility:
            return self._state[8:]
        return RegisterError("Register is not accessible")

    def get_high(self):
        """
        Return the high byte if the register is accessible
        :return: first 8 bits of the register
        """
        if self.accessibility:
            return self._state[:8]
        return RegisterError("Register is not accessible")

    def get(self):
        """
        Returns the state of the register if it is accessible
        :return: all bits of the register
        """
        if self.accessibility:
            return self._state
        return RegisterError("Register is not accessible")

    def __str__(self):
        return self.name

    def __repr__(self):
        return self._state.to01()


class RegisterError(Exception):
    """ Exception raised in register class module """
