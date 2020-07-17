#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0

import os
import argparse


class Simulator:
    """
    Hardware Simulator class.
    Emulates the work of a real computer with:
        * 64kb memory
        * processor registers

    Is supposed to handle a few ISA architectures:
        * Stack
        * Accumulator
        * RISC Register
        * CISC Register architectures

    As well as having a switch between:
        * Memory-Mapped Input/Output
        * Separate space Input/Output

    Has a switch as well to include SIMD instructions (only for CISC)

    Supports a few computer architectures as well:
        * von Neumann
        * Harvard
        * Harvard modified
    """

    def __init__(self):
        """
        Creates new Simulator
        :return: NoneType
        """
        # Creating the argument parser instance and adding the main arguments
        parser = argparse.ArgumentParser()
        parser.add_argument("--file", help="provide the binary code filepath")
        parser.add_argument("--isa",
                            help="specify the ISA architecture: RISC1 (Stack), RISC2 (Accumulator), RISC3 (Register), CISC (Register)",
                            action="store_true")
        parser.add_argument("--architecture",
                            help="specify the data/program architecture: von Neumann, Harvard, HarvardM",
                            action="store_true")
        parser.add_argument("--offset", help="provide the offset for the instructions in the memory")

        # Parsing the command line arguments
        args = parser.parse_args()

        # Lists of valid architecture types
        valid_isa = ['risc1', 'risc2', 'risc3', 'cisc']
        valid_architectures = ['von neumann', 'harvard', 'harvardm']

        # If some of the arguments were not provided, raise an error
        if not args.file:
            raise SimulatorError("Provide the program code binary file")

        if not args.isa or args.isa.lower() not in valid_isa:
            raise SimulatorError("Provide the type of ISA for simulation.")

        if not args.architecture or args.architecture.lower() not in valid_architectures:
            raise SimulatorError("Provide the type of data/program architecture for simulation.")

        self.memory = Memory(args.architecture)
        self.create_registers(args.isa)
        CPU(args.isa, args.file)


class CPU:
    """
    Class for CPU representation
    Actually handles the program logic
    Provides all arithmetics and memory manipulations
    """
    def __init__(self, isa, filename, offset=0):
        """
        Creates a new CPU.
        :param isa: chosen ISA
        :param program_start: location in the memory for the p
        :return: NoneType
        """
        self.isa = isa
        self.load_program(filename, offset)

    def load_program(self, filename, offset):
        """
        Loads the program into memory with an offset given
        Standard location is 1024 bytes
        """
        if not os.path.isfile(filename):
            raise SimulatorError("Provide a valid file path")


    def create_registers(self):
        """
        Create new registers depending on the ISA architecture specified
        :param isa_architecture: chosen ISA
        :return: NoneType
        """
        # Registers common for every ISA architecture
        self.SP = Register()
        self.IP = Register()

        if self.isa.lower() == "risc1":
            pass

        elif self.isa.lower() =="risc2":
            pass

        elif self.isa.lower() =="risc3":
            self.LR = Register()
            self.FR = Register()

            self.R00 = Register(general_purpose=True)
            self.R01 = Register(general_purpose=True)
            self.R02 = Register(general_purpose=True)
            self.R03 = Register(general_purpose=True)

        else:
            pass



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
        self.slots = bytearray(2*1024)


class Register:
    """
    Register simulator class
    Handles the creation of registers of different
    types and their available options
    """

    def __init__(self, general_purpose=False):
        """
        Initializes register object, holding 16 bits,
        specifying its visibility for dev purposes
        """
        self._state = bytearray(2)
        self.accessibility = general_purpose

    def get_low(self):
        """
        Returns the low byte if the register is accessible
        """
        if self.accessibility:
            return self._state[1]
        return SimulatorError("Register is not accessible")

    def get_high(self):
        """
        Return the high byte if the register is accessible
        """
        if self.accessibility:
            return self._state[0]
        return SimulatorError("Register is not accessible")

    def get(self):
        """
        Returns the state of the register if it is accessible
        """
        if self.accessible:
            return self._state
        return SimulatorError("Register is not accessible")


class SimulatorError(Exception):
    pass


if __name__ == '__main__':
    simulator = Simulator()
