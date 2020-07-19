#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0

from bitarray import bitarray


class Memory:
    """
    Memory simulator class
    Handles memory addressing, puts the values and returns them on CPU calls
    Serves as the container for the program code as well
    """

    def __init__(self, memory_architecture):
        """
        Creates a new memory structure.
        :param memory_architecture: chosen program/data architecture.
        :return: NoneType
        """
        self.memory_size = 1024*8
        self.slots = bitarray("0"*self.memory_size)

    def write(self, location, data):
        """
        Writes the data in bytes to the memory starting at location
        :param location: start location, where data should be stored
        :param data: data for writing into the memory
        :return: NoneType
        """
        if (len(data) > (self.memory_size - location)):
            raise MemoryError("Memory overflow")

        self.slots[location*8:location*8+len(data)] = data

    def read_data(self, start_location, end_location):
        return self.slots[start_location:end_location]

    def __str__(self):
        return self.slots


class MemoryError(Exception):
    """ Exception raised in the memory class modules """
