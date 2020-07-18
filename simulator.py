#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0

import os
import json
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
        self.read_state = "opcode"

        self.functions_dict = {}

        with open("instructions.json", "r") as file:
            self.opcodes = json.load(file)[self.isa.lower()]

        with open("registers.json", "r") as file:
            self.registers_list = json.load(file)[self.isa.lower()]

        # Determining the size of the instructions to read
        instruction_sizes = {"risc1": (6, 6), "risc2": (8, 8), "risc3": (16, 6), "cisc": (8, 8)}
        self.instruction_size = instruction_sizes[self.isa.lower]

        # Create the registers for the specified architecture
        self.create_registers()

        # Set the instruction pointer to the starting point of the program
        self.IP = 0 + offset
        self.load_program(filename)

        # Starts the execution of the program code loaded
        self.start_program()

        # Closes the simulator and restores the console settings
        self.close()

    def start_screen(self):
        """
        Draws the screen elements the first time
        """
        self.std_screen = curses.initscr()

        # Setting up the curses module so that keys would not be echoed instantly to the screen
        curses.noecho()
        # Shifting from standard buffer mode to instant action on key press
        curses.cbreak()
        # Turning on keypad mode for easier custom keys support
        self.std_screen.keypad(True)
        # Turning the flickering pointer off
        curses.curs_set(False)

        if curses.has_colors():
            curses.start_color()

        # Initialize a few main color pairs (foreground color, background color)
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)

        # Add title and menu elements
        self.std_screen.addstr("Hardware Simulator", curses.A_REVERSE | curses.color_pair(2))
        self.std_screen.addstr(curses.LINES - 1, 0,
                              "Press 'q' to exit, 'n' to execute the next instruction",
                              curses.A_REVERSE)

        # Create the box for the instruction in binary
        self.instruction_window = curses.newwin(3, 19, 5, 2)
        self.instruction_window.box()
        # Create the sub-window for the actual instruction in binary representation
        self.instruction_box = self.instruction_window.subwin(1, 17, 6, 3)

        # Create the box for the registers info
        self.register_window = curses.newwin(11, 24, 5, 30)
        self.register_window.box()
        # Create the sub-window for the actual registers representation
        self.register_box = self.register_window.subwin(9, 22, 6, 31)

        # Fill the register box with current registers and their values
        self.register_box.addstr(" Registers:\n")
        items = [(value.name, value._state.hex()) for key, value in self.registers.items()]
        for i in range(1, len(items)):
            self.register_box.addstr(f" {(items[i-1][0]+':').ljust(4, ' ')} {items[i-1][1]}  "
                                     f"{(items[i][0]+':').ljust(4, ' ')} {items[i][1]}\n")

        # Refresh all the internal datastructures bottom-up, update the screen
        self.std_screen.noutrefresh()
        self.instruction_window.noutrefresh()
        self.register_window.noutrefresh()
        self.instruction_box.noutrefresh()
        self.register_box.noutrefresh()
        curses.doupdate()

    def create_registers(self):
        """
        Create new registers depending on the ISA architecture specified
        :param isa_architecture: chosen ISA
        :return: NoneType
        """
        self.registers = dict()
        self.register_codes = dict()

        for register in self.registers_list:
            temp = Register(register[0], general_purpose=(register[1]==1))
            self.registers[register[2]] = temp
            self.register_codes[register[2]] = temp

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
        # Read first instruction of the program from the memory
        self.instruction = self.memory.read_data(self.IP, self.IP+self.instruction_size[0])

        # Continue executing instructions until we reach
        # the end of the program (all-zeros byte)
        while bytes(self.instruction) != b"\0"*16:

            # Draw the updated screen
            self.draw_screen()

            key = ''

            # Move on to the next instruction if the 'n' key is pressed
            while key not in ('N', 'n'):
                key = self.instruction_window.getkey()

                # Finish the program if the 'q' key is pressed
                if key in ('Q', 'q'):
                    return

            # Execute this instruction, and move on to the next one, reading it
            self.execute()
            self.IP += 16
            self.instruction = self.memory.read_data(self.IP, self.IP+self.instruction_size[0])

    def execute(self):
        """
        Executes an instruction
        :param instruction: binary instruction to be executed
        :return: NoneType
        """
        opcode_dict = dict()
        for key in self.opcodes:
            opcode_dict[self.opcodes[key][0:]] = tuple([key] + [self.opcodes[key][1

        # Read the opcode part of the instruction
        if self.read_state == "opcode":
            self.opcode = self.instruction[0:self.instruction_size[0]]
        elif self.read_state == "constant1":
            pass
        elif self.read_state == "constant2":
            pass

        # Figure out the operands for the RISC-Stack ISA
        if self.isa.lower() == "risc1":
            pass

        # Figure out the operands for the RISC-Accumulator ISA
        if self.isa.lower() == "risc2":
            pass

        # Figure out the operands for the RISC-Register ISA
        if self.isa.lower() == "risc3":

            # TODO: create more groups of instructions depending on the
            #  size of the immediate constant and the start of the operands

            # Load the special case moves for RISC-Register architecture
            low_high_load_risc = ["mov_low1", "mov_low2", "mov_high1", "mov_high2"]
            low_high_load_risc = [self.opcodes.get(name)[0] for name in low_high_load_risc]

            # Load low/high bytes check for RISC-register architecture
            if self.opcode in low_high_load_risc:
                start_point = 5
                immediate_length = 8
            else:
                start_point = 6
                immediate_length = 8

        # Figure out the operands for the CISC-Register ISA
        if self.isa.lower() == "cisc":
            pass

        # Read all the operands after the opcode
        operands = []
        operands_aliases = opcode_dict[self.opcode][1:]
        for operand in operands_aliases:

            # If the operand is the register, add its value and go to the next operand
            if operand == "reg":
                operands.append(self.register_codes[self.instruction[start_point+3]]._state)
                start_point += 3

            # If the operand is the memory addressed by register, add its value and go to the next operand
            elif operand == "memreg":
                tmp_register = self.register_codes[self.instruction[start_point+3]]._state
                operands.append(self.memory.read_data(tmp_register, tmp_register + self.instruction_size[0]))
                start_point += 3

            # If the operand is the immediate constant, add its value and go to the next operand
            elif operand == "imm":
                operands.append(immediate)
                start_point += immediate_length

        # Execute needed function and save its result to the first operand
        function = functions_dict[opcode_dict[self.opcode][0]]
        operands[0] = function(operands)

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

    def access_value(self, parameter):
        """
        Access value depending on a parametr
        """


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

    def __init__(self, name, general_purpose=False):
        """
        Initializes register object, holding 16 bits,
        specifying its visibility for dev purposes
        :return: NoneType
        """
        self.name = name
        self._state = bytearray(2)
        self.accessibility = general_purpose

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


class SimulatorError(Exception):
    """ Exception raised in Hardware Simulator modules """


if __name__ == '__main__':
    simulator = Simulator()
