#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0

from bitarray import bitarray


class Shell:
    """
    Class for shell representation
    """
    def __init__(self, io_type, start=0, end=0):
        """
        Create new shell

        :param io_type: I/O type (MMIO, special commands)
        :return: NoneType
        """
        self.start_point = start
        self.end_point = end
        self.io_type = io_type
        self._state = bitarray("0"*160)

    def in_shell(self):
        # TODO: implement input
        #  UPD: I think we have?!
        pass

    def out_shell(self, value):
        """
        Write value into the shell (to the right)

        :param value: value to be written
        """
        self._state += value[-8:]
        self._state = self._state[-160:]

    def __str__(self):
        """
        Return string representation of the shell's contents

        :return: ascii-decoded slots of the shell
        """
        data = bitarray(self._state.to01())

        # Clean the data so there would not be any null characters
        for i in range(0, len(self._state), 8):
            if data[i:i+8].to01() == "00000000":
                data[i:i+8] = bitarray("00100000")

        return data.tobytes().decode("ascii")
