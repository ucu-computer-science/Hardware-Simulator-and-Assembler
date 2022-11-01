#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0
import os
import argparse

from modules.processor import CPU, SimulatorError


class Simulator:
    """
    CLI Simulator Interface
    """

    def __init__(self):
        """
        Creates a new Simulator instance
        :return: NoneType
        """
        # Creating the argument parser instance and adding the main arguments
        parser = argparse.ArgumentParser()
        parser.add_argument("--file", help="provide the binary code filepath")
        parser.add_argument("--isa",
                            help="specify the ISA architecture: Stack, Accumulator, RISC (Register), CISC (Register)")
        parser.add_argument("--architecture",
                            help="specify the data/program architecture: neumann, harvard, harvardm")
        parser.add_argument("--output", help="specify the type of I/O: mmio, special")
        parser.add_argument("--program_start", help="provide the program_start for the instructions in the memory")

        # Parsing the command line arguments
        args = parser.parse_args()

        # Lists of valid architecture types
        valid_isa = ['stack', 'accumulator', 'risc', 'cisc']
        valid_architectures = ['neumann', 'harvard', 'harvardm']
        valid_io = ['mmio', 'special']

        # If some of the arguments were not provided, raise an error
        if not args.file:
            raise SimulatorError("Provide the program code binary file")

        if not os.path.isfile(args.file):
            raise SimulatorError("Provide a valid file path")

        with open(args.file, "r") as file:
            program_text = file.read()

        if not args.isa or args.isa.lower() not in valid_isa:
            raise SimulatorError("Provide the type of ISA for simulation.")

        if not args.architecture or args.architecture.lower() not in valid_architectures:
            raise SimulatorError("Provide the type of data/program architecture for simulation.")

        if not args.output or args.output.lower() not in valid_io:
            raise SimulatorError("Provide the type of Input/Output architecture for simulation")

        CPU(args.isa.lower(), args.architecture.lower(), args.output.lower(), program_text, curses_mode=True)


if __name__ == '__main__':
    simulator = Simulator()
