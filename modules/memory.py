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

    def __init__(self, size):
        """
        Creates a new memory structure.
        :param memory_architecture: chosen program/data architecture.
        :return: NoneType
        """
        self.memory_size = size*8
        self.slots = bitarray("0"*self.memory_size)

    def write(self, location, data):
        """
        Writes the data in bytes to the memory starting at location
        :param location: start location (bytes), where data should be stored
        :param data: data for writing into the memory
        :return: NoneType
        """
        if (len(data) > (self.memory_size - location)):
            raise MemoryError("Memory overflow")

        self.slots[location*8:location*8+len(data)] = data

    def read_data(self, start_location, end_location):
        """
        Reads the data from memory [start_location:end_location]
        :param start_location: int - starting location in bits
        :param end_location: int - end location in bits
        """
        return self.slots[start_location:end_location]

    def __str__(self):
        """ Returns a representation of its contents in bitarray"""
        return self.slots


class MemoryError(Exception):
    """ Exception raised in the memory class modules """
