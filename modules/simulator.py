#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0

import os
import json
import os
import argparse
import curses
import logging
from bitarray import bitarray
from bitarray.util import ba2hex

from modules.functions import functions_dictionary, twos_complement
from modules.memory import Memory
from modules.register import Register

logging.basicConfig(filename="log.txt",
                    filemode='w',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger('logger')


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

        with open(os.path.join("modules", "instructions.json"), "r") as file:
            self.opcode_dict = json.load(file)[self.isa.lower()]

        with open(os.path.join("modules", "registers.json"), "r") as file:
            self.registers_list = json.load(file)[self.isa.lower()]

        # Determining the size of the instructions to read
        instruction_sizes = {"risc1": (6, 6, 1), "risc2": (8, 8, 1), "risc3": (16, 6, 2), "cisc": (8, 8, 1)}
        self.instruction_size = instruction_sizes[self.isa.lower()]

        # Create the registers for the specified architecture
        self.create_registers()

        # Set the instruction pointer to the starting point of the program
        self.registers["IP"]._state = bitarray(bin(twos_complement(128 + offset, 16))[2:].rjust(16, '0'))
        self.load_program(filename)

        # Draw the main interface
        self.start_screen()

        # Starts the execution of the program code loaded
        close_program = self.start_program()

        key = ''
        # Closes the simulator and restores the console settings
        while key not in ('Q', 'q') and not close_program:
            key = self.instruction_window.getkey()

        self.close()
        print(len(self.memory.slots))

    def create_registers(self):
        """
        Create new registers depending on the ISA architecture specified
        :param isa_architecture: chosen ISA
        :return: NoneType
        """
        self.registers = dict()
        self.register_codes = dict()

        for register in self.registers_list:
            temp = Register(register[0], general_purpose=(register[1] == 1))
            self.registers[register[0]] = temp
            self.register_codes[register[2]] = temp

    def load_program(self, filename):
        """
        Loads the program into memory at Instruction Pointer
        """
        if not os.path.isfile(filename):
            raise SimulatorError("Provide a valid file path")

        # Writing program instructions into to memory
        with open(filename, "r") as file:
            self.memory.write(twos_complement(int(self.registers["IP"]._state.to01(), 2), 16), bitarray(file.read().replace('\n', '')))

    def start_program(self):
        """
        Handles the execution of the actual program
        :return: NoneType
        """
        # Read first instruction of the program from the memory
        self.__read_instruction()

        # Continue executing instructions until we reach
        # the end of the program (all-zeros byte)
        while self.instruction != bitarray('0' * 16):
            key = ''

            # Draw the updated screen
            self.draw_screen()

            # Move on to the next instruction if the 'n' key is pressed
            while key not in ('N', 'n'):
                key = self.instruction_window.getkey()

                # Finish the program if the 'q' key is pressed
                if key in ('Q', 'q'):
                    return True

            # Execute this instruction, and move on to the next one, reading it
            self.execute()
            ip_value = twos_complement(int(self.registers["IP"]._state.to01(), 2) + 2, 16)
            self.registers["IP"]._state = bitarray(bin(ip_value)[2:].rjust(16, '0'))
            self.__read_instruction()

        # Draw the updated screen
        self.draw_screen()

    def __read_instruction(self):
        """
        Reads the instruction and the opcode in it
        """
        start_read_location = twos_complement(int(self.registers["IP"]._state.to01(), 2), 16)
        self.instruction = self.memory.read_data(start_read_location, start_read_location + self.instruction_size[2])

        # Read the opcode part of the instruction
        if self.read_state == "opcode":
            self.opcode = self.instruction[0:self.instruction_size[1]]
        elif self.read_state == "constant1":
            pass
        elif self.read_state == "constant2":
            pass

    def execute(self):
        """
        Executes an instruction
        :param instruction: binary instruction to be executed
        :return: NoneType
        """

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
            low_high_load_risc = ["mov_low", "mov_high"]
            low_high_load_risc = [bitarray(code) for code in self.opcode_dict if self.opcode_dict[code][0] in low_high_load_risc]

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
        # Making sure, that the first one specifies destination of the operation
        operands_aliases = self.opcode_dict[self.opcode.to01()][1]
        operands = [self.register_codes[self.instruction[start_point:start_point + 3].to01()]]

        # Set 'write' access to the memory to False by default
        memory_write_access = False

        # If destination -> memory
        if operands_aliases[0] == "memreg":
            memory_write_access = True

        for operand in operands_aliases:

            # If the operand is the register, add its value and go to the next operand
            if operand == "reg":
                operands.append(self.register_codes[self.instruction[start_point:start_point + 3].to01()]._state)
                start_point += 3

            # If the operand is the memory addressed by register, add its value and go to the next operand
            elif operand == "memreg":
                tmp_register = int(self.register_codes[self.instruction[start_point:start_point + 3].to01()]._state.to01(), 2)
                operands.append(self.memory.read_data(tmp_register, tmp_register + self.instruction_size[0]))
                start_point += 3

            # If the operand is the immediate constant, add its value and go to the next operand
            elif operand[:3] == "imm":
                immediate_length = int(operand[3:])
                operands.append(bitarray(self.instruction[start_point:start_point + immediate_length]))
                start_point += immediate_length

        # Execute needed function and save its result to the first operand
        function = functions_dictionary[self.opcode_dict[self.opcode.to01()][0]]

        # Pass Flag register to the function
        operands.append(self.registers["FR"])

        # Write into the memory
        if memory_write_access:
            self.memory.write(int(operands[0]._state.to01(), 2), function(operands))
        # Perform any other instruction
        else:
            function(operands)

    def start_screen(self):
        """
        Draws the screen elements the first time
        """
        # Setting up the curses module so that keys would not be echoed instantly to the screen
        self.std_screen = curses.initscr()
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
        self.instruction_window = curses.newwin(5, 19, 2, 2)
        self.instruction_window.box()
        # Create the sub-window for the actual instruction in binary representation
        self.instruction_box = self.instruction_window.subwin(3, 17, 3, 3)

        # Create the box for the registers info
        self.register_window = curses.newwin(8, 25, 2, 30)
        self.register_window.box()
        # Create the sub-window for the actual registers representation
        self.register_box = self.register_window.subwin(6, 23, 3, 31)

        # Create the box for the memory representation
        self.memory_window = curses.newwin(19, 130, 10, 2)
        self.memory_window.box()
        # Create the window for the memory print
        self.memory_box = self.memory_window.subwin(17, 128, 11, 3)

        # Refresh all the internal datastructures bottom-up, update the screen
        self.std_screen.noutrefresh()
        self.instruction_window.noutrefresh()
        self.register_window.noutrefresh()
        self.memory_window.noutrefresh()
        curses.doupdate()

    def draw_screen(self):
        """
        Updates the contents of the screen
        :return: NoneType
        """

        # Clearing the instruction box and inserting the new instruction
        self.instruction_box.clear()
        self.instruction_box.addstr("Next instruction:")
        self.instruction_box.addstr(f"{self.instruction.to01()}\n")
        self.instruction_box.addstr(self.opcode_dict[self.opcode.to01()][0])

        # Fill the register box with current registers and their values
        self.register_box.clear()
        self.register_box.addstr(" Registers:\n")
        items = [(value.name, value._state.tobytes().hex()) for key, value in self.registers.items()]
        for i in range(1, len(items), 2):
            self.register_box.addstr(f" {(items[i - 1][0] + ':').ljust(4, ' ')} {items[i - 1][1]}  "
                                     f"{(items[i][0] + ':').ljust(4, ' ')} {items[i][1]}\n")

        # Refresh the memory on screen
        self.memory_box.clear()
        for i in range(0, len(self.memory.slots), 8):
            self.memory_box.addstr(ba2hex(self.memory.slots[i:i+8]))

        # Refreshing the contents of screen elements and updating the whole screen
        self.std_screen.noutrefresh()
        self.instruction_box.noutrefresh()
        self.register_box.noutrefresh()
        self.memory_box.noutrefresh()
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


class SimulatorError(Exception):
    """ Exception raised in Hardware Simulator modules """


if __name__ == '__main__':
    simulator = Simulator()
