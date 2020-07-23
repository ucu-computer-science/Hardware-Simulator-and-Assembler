#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0


import os
import argparse
import logging

from modules.processor import CPU, SimulatorError

# Set up the logging module so it would save everything to a file
# (we are unable to track prints in real-time due to curses)
logging.basicConfig(filename="log.txt",
                    filemode='w',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger('logger')
# TODO: Add new logging statements
#
# TODO: Massively refactor and clean up this file, start with getting CPU into its own module


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
                            help="specify the ISA architecture: RISC1 (Stack), RISC2 (Accumulator), RISC3 (Register), CISC (Register)")
        parser.add_argument("--architecture",
                            help="specify the data/program architecture: neumann, harvard, harvardm")
        parser.add_argument("--output", help="specify the type of I/O: mmio, special")
        parser.add_argument("--offset", help="provide the offset for the instructions in the memory")

        # Parsing the command line arguments
        args = parser.parse_args()

        # Lists of valid architecture types
        valid_isa = ['risc1', 'risc2', 'risc3', 'cisc']
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
