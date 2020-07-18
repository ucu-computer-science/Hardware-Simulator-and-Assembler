#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0

import os
import argparse
import curses
from curses import wrapper

# from functions import functions_dictionary


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
                            help="specify the ISA architecture: RISC1 (Stack), RISC2 (Accumulator), RISC3 (Register), CISC (Register)")
        parser.add_argument("--architecture",
                            help="specify the data/program architecture: von Neumann, Harvard, HarvardM")
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

        CPU(args.isa, args.architecture, args.file)


class CPU:
    """
    Class for CPU representation
    Actually handles the program logic
    Provides all arithmetics and memory manipulations
    """
    def __init__(self, isa, architecture, filename, offset=0):
        """
        Creates a new CPU.
        :param isa: chosen ISA
        :param program_start: location in the memory for the p
        :return: NoneType
        """
        self.isa = isa
        self.memory = Memory(architecture)
        self.instruction = ''

        self.functions_dict = {}

        self.std_screen = curses.initscr()

        # Setting up the curses module so that keys would not be echoed instantly to the screen
        # curses.noecho()
        # # Shifting from standard buffer mode to instant action on key press
        # curses.cbreak()
        # # Turning on keypad mode for easier custom keys support
        # self.std_screen.keypad(True)
        # # Turning the flickering pointer off
        # curses.curs_set(False)
        #
        # if curses.has_colors():
        #     curses.start_color()
        #
        # # Initialize a few main color pairs (foreground color, background color)
        # curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        # curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        # curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        #
        # # Add title and menu elements
        # self.std_screen.addstr("Hardware Simulator", curses.A_REVERSE | curses.color_pair(2))
        # self.std_screen.addstr(curses.LINES - 1, 0,
        #                       "Press 'q' to exit",
        #                       curses.A_REVERSE)
        #
        # # Create the box for the instruction in binary
        # self.instruction_window = curses.newwin(3, 19, 5, 2)
        # self.instruction_window.box()
        # # Create the sub-window for the actual instruction in binary representation
        # self.instruction_box = self.instruction_window.subwin(1, 17, 6, 3)
        #
        # # Create the box for the registers info
        # self.register_window = curses.newwin(11, 64, 5, 30)
        # self.register_window.box()
        # # Create the sub-window for the actual registers representation
        # self.register_box = self.register_window.subwin(9, 60, 6, 31)

        # Create the registers for the specified architecture
        self.create_registers()

        # Sets the instruction pointer to the starting point of the program
        self.IP = 0 + offset
        self.load_program(filename)

        # Refresh all the internal datastructures bottom-up, update the screen
        # self.std_screen.noutrefresh()
        # self.instruction_window.noutrefresh()
        # self.register_window.noutrefresh()
        # self.instruction_box.noutrefresh()
        # self.register_box.noutrefresh()
        # curses.doupdate()

        items = [(key, value._state.hex()) for key, value in self.registers_dict.items()]
        for i in range(1, len(items)):
            print(f"{items[i-1][0]}: {items[i-1][1]}  {items[i][0]}: {items[i][1]}\n")

        self.start_program()

        # Closes the simulator and restores the console settings
        self.close()

    def create_registers(self):
        """
        Create new registers depending on the ISA architecture specified
        :param isa_architecture: chosen ISA
        :return: NoneType
        """
        # Registers common for every ISA architecture
        self.registers_dict = dict()
        self.SP = Register(self.memory)
        self.registers_dict[b'100'] = self.SP
        self.IP = Register(self.memory)
        self.registers_dict[b'101'] = self.IP

        # Setting up "RISC-Stack" ISA registers
        if self.isa.lower() == "risc1":
            pass

        # Setting up "RISC-Accumulator" ISA registers
        elif self.isa.lower() =="risc2":
            pass

        # Setting up "RISC-Register" ISA registers
        elif self.isa.lower() =="risc3":

            # Link Register
            self.LR = Register(self.memory)
            self.registers_dict[b'110'] = self.LR

            # Flag Register
            self.FR = Register(self.memory)
            self.registers_dict[b'111'] = self.FR

            # Setting up general purpose R00-R03 registers
            self.R00 = Register(self.memory, general_purpose=True)
            self.registers_dict[b'000'] = self.R00
            self.R01 = Register(self.memory, general_purpose=True)
            self.registers_dict[b'001'] = self.R01
            self.R02 = Register(self.memory, general_purpose=True)
            self.registers_dict[b'010'] = self.R02
            self.R03 = Register(self.memory, general_purpose=True)
            self.registers_dict[b'011'] = self.R03

        # Setting up "CISC-Register" ISA registers
        else:
            pass

    def load_program(self, filename):
        """
        Loads the program into memory at Instruction Pointer
        """
        if not os.path.isfile(filename):
            raise SimulatorError("Provide a valid file path")

        # Writing program instructions into to memory
        with open(filename, "rb") as file:
            self.memory.write(self.IP, file.read().strip(b'\n'))

    def start_program(self):
        """
        Handles the execution of the actual program
        :return: NoneType
        """
        # Determining the size of the instruction to read
        instruction_sizes = {"risc1": 6, "risc2": 8, "risc3": 16, "risc4": 8}
        instruction_size = instruction_sizes[self.isa.lower()]

        # Read first instruction of the program from the memory
        self.instruction = self.memory.read_data(self.IP, self.IP+16)

        # Continue executing instructions until we reach
        # the end of the program (all-zeros byte)
        while bytes(self.instruction) != b"\0"*16:

            # Draw the updated screen
            # self.draw_screen()

            key = ''

            # Move on to the next instruction if the 'n' key is pressed
            while key not in ('N', 'n'):
                # key = self.instruction_window.getkey()

                # Finish the program if the 'q' key is pressed
                if key in ('Q', 'q'):
                    return

            # Execute this instruction, and move on to the next one, reading it
            self.execute()
            self.IP += 16
            self.instruction = self.memory.read_data(self.IP, self.IP+16)

    def execute(self):
        """
        Executes an instruction
        :param instruction: binary instruction to be executed
        :return: NoneType
        """
        opcode = self.instruction[0:6]

        # Load immediate constant
        if opcode[0:3] == b"00":
            reg_code = self.instruction[5:8]
            immediate = self.instruction[8:]

            # Load low byte
            if opcode[0:5] == b"00001":
                self.self.registers_dict[reg_code]._state[8:] = immediate
            # Load high byte
            else:
                self.self.registers_dict[reg_code]._state[:8] = immediate

        # For three registers (dest = src1, src2)
        elif opcode[0:3] == b"01":
            reg1_code = self.instruction[6:9]
            reg2_code = self.instruction[9:12]
            reg3_code = self.instruction[12:15]

            self.registers_dict[reg1_code]._state = functions_dict[opcode](
                                                self.registers_dict[reg2_code],
                                                self.registers_dict[reg3_code])


        # For a register and immediate constant
        elif opcode[0:3] == b"10":
            reg_code = self.instruction[6:9]
            immediate = self.instruction[9:]

        # For immediate constant
        else:
            immediate = self.instruction[6:]

    def draw_screen(self):
        """
        Updates the contents of the screen
        :return: NoneType
        """

        # TODO: Code snippets for me to check tomorrow
        # delch(cur_pos[0], cur_pos[1]-1)
        # addch(node.char)

        # Clearing the instruction box and inserting the new instruction
        self.instruction_box.clear()
        print(self.instruction.decode())
        self.instruction_box.addstr(self.instruction.decode())

        # Refreshing the contents of screen elements and updating the whole screen
        self.std_screen.noutrefresh()
        self.instruction_window.noutrefresh()
        self.instruction_box.noutrefresh()
        self.register_window.noutrefresh()
        self.register_box.noutrefresh()
        curses.doupdate()

    def close(self):
        """
        Finishes the execution of the program, clearing the
        settings set by curses for proper terminal work
        :return: NoneType
        """
        curses.echo()
        curses.nocbreak()
        self.std_screen.keypad(False)
        curses.curs_set(True)
        curses.endwin()


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
        self.memory_size = 2*1024
        self.slots = bytearray(self.memory_size)

    def write(self, location, data):
        """
        Writes the data in bytes to the memory starting at location
        :param location: start location, where data should be stored
        :param data: data for writing into the memory
        :return: NoneType
        """
        if (len(data) > (self.memory_size - location)):
            raise SimulatorError("Memory overflow")

        self.slots[location:len(data)] = data

    def read_data(self, start_location, end_location):
        return self.slots[start_location:end_location]

    def __str__(self):
        return self.slots


class Register:
    """
    Register simulator class
    Handles the creation of registers of different
    types and their available options
    """

    def __init__(self, name, memory_slots, general_purpose=False):
        """
        Initializes register object, holding 16 bits,
        specifying its visibility for dev purposes
        :return: NoneType
        """
        self.name = name
        self._state = bytearray(2)
        self.accessibility = general_purpose
        self.memory_slots = memory_slots

    def get_low(self):
        """
        Returns the low byte if the register is accessible
        :return: last 8 bits of the register
        """
        if self.accessibility:
            return self._state[1]
        return SimulatorError("Register is not accessible")

    def get_high(self):
        """
        Return the high byte if the register is accessible
        :return: first 8 bits of the register
        """
        if self.accessibility:
            return self._state[0]
        return SimulatorError("Register is not accessible")

    def get(self):
        """
        Returns the state of the register if it is accessible
        :return: all bits of the register
        """
        if self.accessible:
            return self._state
        return SimulatorError("Register is not accessible")

    def get_from_memory(self):
        """
        Return data from memory,
        regarding state of the register as location in memory.
        """
        return self.memory_slots[int(self._state)]


class SimulatorError(Exception):
    """ Exception raised in Hardware Simulator modules """


if __name__ == '__main__':
    simulator = Simulator()
