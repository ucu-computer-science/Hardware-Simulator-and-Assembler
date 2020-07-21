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
from modules.shell import Shell

# Set up the logging module so it would save everything to a file
# (we are unable to track prints in real-time due to curses)
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


class CPU:
    """
    Class for CPU representation
    Actually handles the program logic
    Provides all arithmetics and memory manipulations
    """

    def __init__(self, isa, architecture, io_arch, program_text, offset=0, curses_mode=False):
        """
        Creates a new CPU.
        :param isa: chosen ISA
        :param architecture: chosen Architecture type
        :param io_arch: chosen Input/Output type
        :param program_text: str - text of the binary program file
        :param offset: location in the memory for the program code, as an offset from default
        :return: NoneType
        """
        self.isa = isa
        self.architecture = architecture
        self.io_arch = io_arch
        self.curses_mode = curses_mode

        # Create devices for this CPU depending on the I/O architecture specified
        if io_arch == "mmio":
            shell = Shell(io_arch, start=1004, end=1024)
        else:
            shell = Shell(io_arch)
        self.ports_dictionary = {"1": shell}

        # Opening the instruction set and choosing the one for our chosen ISA architecture
        with open(os.path.join("modules", "instructions.json"), "r") as file:
            self.instructions_dict = json.load(file)[self.isa]

        # Determining the size of the instructions to read (size of the instruction, opcode size, instruction in bytes)
        instruction_sizes = {"risc1": (6, 6, 1), "risc2": (8, 8, 1), "risc3": (16, 6, 2), "cisc": (8, 8, 1)}
        self.instruction_size = instruction_sizes[self.isa]

        # Create the registers for the specified register architecture
        self.__create_registers()

        # Create data and program memory according to the specified architecture
        if architecture in ["neumann", "harvardm"]:
            memory = Memory(1024)
            self.data_memory = memory
            self.program_memory = memory
        elif architecture == "harvard":
            self.data_memory = Memory(512)
            self.program_memory = Memory(512)

        # Set the instruction pointer to the starting point of the program and load the specified program into memory
        self.registers["IP"]._state = bitarray(bin(twos_complement(128 + offset, 16))[2:].rjust(16, '0'))
        self.__load_program(program_text)
        self.read_state = "opcode"

        # Draw the main interface
        if self.curses_mode:
            self.start_screen()

            # Starts the execution of the program code loaded
            is_close_program = self.start_program()

            # Closes the simulator and restores the console settings
            key = ''
            while key not in ('Q', 'q') and not is_close_program:
                key = self.instruction_window.getkey()

            # Close the curses module screen if we are in its mode
            self.close_screen()

    def __create_registers(self):
        """
        Create new registers depending on the ISA architecture specified
        :return: NoneType
        """
        with open(os.path.join("modules", "registers.json"), "r") as file:
            registers_list = json.load(file)[self.isa]

        self.registers = dict()
        self.register_codes = dict()

        for register in registers_list:
            temp = Register(register[0], general_purpose=(register[1] == 1))
            self.registers[register[0]] = temp
            self.register_codes[register[2]] = temp

    def __load_program(self, program_text):
        """
        Loads the program into memory at Instruction Pointer
        :param program_text: str - text of the binary program file
        """
        # Writing program instructions into to memory
        ip_value = twos_complement(int(self.registers["IP"]._state.to01(), 2), 16)
        self.program_memory.write(ip_value, bitarray(program_text.replace('\n', '')))

    def start_program(self):
        """
        Handles the execution of the actual program
        :return: NoneType
        """
        # Continue executing instructions until we reach
        # the end of the program (all-zeros byte)
        while True:

            # Read first instruction of the program from the memory
            self.__read_instruction()

            # Update the Memory-Mapped devices
            self.__update_devices()

            # Draw the updated screen
            if self.curses_mode:
                logger.info("Drawing the screen")
                self.draw_screen()

            if self.instruction.to01() == ('0' * 16):
                return False

            logger.info("Entering execute cycle")
            is_close = self.__execute_cycle()
            if is_close:
                return True

    def __execute_cycle(self):
        """
        Execute the current instruction, and move on to the next one
        """
        is_close = False
        # Waiting for the key or button to be pressed, depending on the mode
        if self.curses_mode:
            is_close = self.curses_next_instruction()

        self.execute()
        logger.info("Executing the instruction. To close: " + str(is_close))
        ip_value = twos_complement(int(self.registers["IP"]._state.to01(), 2) + 2, 16)
        self.registers["IP"]._state = bitarray(bin(ip_value)[2:].rjust(16, '0'))

        return is_close

    def web_next_instruction(self):
        """
        Executes the next instruction after button click on the webpage
        """
        if self.instruction.to01() == ('0' * 16):
            return

        # Read first instruction of the program from the memory
        self.__read_instruction()
        # Execute the cycle
        self.__execute_cycle()

        # Update the Memory-Mapped devices
        self.__update_devices()

    def __update_devices(self):
        """
        Updates the devices if they are Memory-Mapped
        """
        for port, device in self.ports_dictionary.items():
            if device.io_type == "mmio":
                data = self.data_memory.read_data(device.start_point, device.end_point)
                device._state = data

    def __read_instruction(self):
        """
        Reads the instruction and the opcode in it
        """
        start_read_location = twos_complement(int(self.registers["IP"]._state.to01(), 2), 16)
        self.instruction = self.program_memory.read_data(start_read_location, start_read_location + self.instruction_size[2])

        # Read the opcode part of the instruction
        if self.read_state == "opcode":
            self.opcode = self.instruction[0:self.instruction_size[1]]
        elif self.read_state == "constant1":
            pass
        elif self.read_state == "constant2":
            pass

    def execute(self):
        """
        Executes an instruction, decoding its operands, computing the
        result and saving it in the proper place
        :return: NoneType
        """
        # TODO: This method is still super huge, we are going to probably have to break it up

        # Determine the point in the binary instruction where operands start
        start_point = self.__determine_start_point()

        # Reading the list of operands encoded in the binary instruction
        operands_aliases = self.instructions_dict[self.opcode.to01()][-1]

        # Determine whether the memory is going to be affected as a
        # result of the operation and where to save it
        memory_write_access, result_destination = self.__determine_result_dest(start_point, operands_aliases)

        # Add operands values to the list to provide to a function later
        operands_values = []
        for operand in operands_aliases:

            # If the operand is the register, add its value and go to the next operand
            if operand == "reg":
                register_code = self.instruction[start_point:start_point + 3].to01()
                operands_values.append(self.register_codes[register_code]._state)
                start_point += 3

            # If the operand is the memory addressed by register, add its value and go to the next operand
            elif operand == "memreg":
                register_code = self.instruction[start_point:start_point + 3].to01()
                tmp_register = twos_complement(int(self.register_codes[register_code]._state.to01(), 2), 16)
                operands_values.append(self.data_memory.read_data(tmp_register, tmp_register + self.instruction_size[0]))
                start_point += 3

            # If the operand is the immediate constant, add its value and go to the next operand
            elif operand.startswith("imm"):
                immediate_length = int(operand[3:])
                operands_values.append(bitarray(self.instruction[start_point:start_point + immediate_length]))
                start_point += immediate_length

        # PROCESSING THE ACTUAL INSTRUCTION BELOW
        # If the opcode type is call, we can perform the needed actions without calling functions_dict
        if (res_type := self.instructions_dict[self.opcode.to01()][1]) == "call":

            # Remember the next instruction after the one which called the 'call' function
            next_instruction = int(self.registers["IP"]._state.to01(), 2)
            self.registers["LR"]._state = bitarray(bin(twos_complement(next_instruction, 16))[2:].rjust(16, '0'))

            # There is only one operand for a call function, and it determines the offset from the IP
            operand = operands_aliases[0]
            if operand.startswith("imm"):

                # TODO: This implies that instructions take up 16 bits (2 bytes), which is rarely true
                imm_len = int(operand[3:])
                offset = twos_complement(int(operands_values[0].to01(), 2), imm_len) * 2
                ip_value = int(self.registers["IP"]._state.to01(), 2)
                self.registers["IP"]._state = bitarray(bin(ip_value + offset - 2)[2:].rjust(16, '0'))

            # There is only one operand for a call function, and it determines an absolute address in the memory
            elif operand == "reg":
                self.registers["IP"]._state = operands_values[0]

        # If the opcode type is return, we just move the instruction pointer back
        elif res_type == "ret":

            # TODO: Should we zero out the Link Register register after returning to it once?
            self.registers["IP"]._state = self.registers["LR"]._state

        # If the opcode is of type jump, we look at the Flag Register and move Instruction Pointer if needed
        elif res_type == "jmp":

            # Set jump by default to False
            should_jump = False
            flag_reg = self.registers["FR"]._state
            carry_flag, zero_flag, overflow_flag, sign_flag = flag_reg[-4:]

            # Check the needed flags according to the jump condition specified
            if (jmp_spec := self.instructions_dict[self.opcode.to01()][0]) == "jmp":
                should_jump = True
            elif jmp_spec == "je":
                should_jump = zero_flag
            elif jmp_spec == "jne":
                should_jump = not zero_flag
            elif jmp_spec == "jg":
                should_jump = (sign_flag == overflow_flag) and not zero_flag
            elif jmp_spec == "jge":
                should_jump = (sign_flag == overflow_flag)
            elif jmp_spec == "jl":
                should_jump = (sign_flag != overflow_flag)
            elif jmp_spec == "jle":
                should_jump = (sign_flag == overflow_flag) or zero_flag

            # If the jump condition was satisfied, jump to the value specified with the operand
            if should_jump:

                # If the offset was specified with the number, its length was specified as well
                if operands_aliases[0].startswith("imm"):
                    num_len = int(operands_aliases[0][3:])
                else:
                    # Else, just use the register length
                    num_len = 16

                # TODO: This implies that instructions take up 16 bits (2 bytes), which is rarely true
                offset = twos_complement(int(operands_values[0].to01(), 2), num_len) * 2
                ip_value = int(self.registers["IP"]._state.to01(), 2)
                self.registers["IP"]._state = bitarray(bin(ip_value + offset - 2)[2:].rjust(16, '0'))

        # If the opcode specified pushes the value on the stack
        elif res_type == "stackpush":
            self.__push_stack(operands_values[0])

        # If the opcode specified pops the value from the stack into the register
        elif res_type == "stackpop":
            result_destination._state = self.__pop_stack()

        # If the opcode specifies outputting to the device
        elif res_type == "out":
            result_destination.out_shell(operands_values[-1])

        # Else, we have to execute the needed computations for this function in the virtual ALU
        else:
            # Determine the needed function for this opcode and execute it, passing the flag register
            function = functions_dictionary[self.instructions_dict[self.opcode.to01()][0]]
            result_value = function(operands_values, flag_register=self.registers["FR"])

            # Write the result of the operation into the memory
            if memory_write_access:
                self.data_memory.write(result_destination, result_value)
            # Write into the result destination
            else:
                result_destination._state = bitarray(result_value)

    def __determine_start_point(self):
        """
        Determines the start point of the operands in theinstruction and other details
        depending on the ISA architecture

        The helper function for the 'execute' method

        :return: start_point - int, representing the bit value in the instruction from which the opcodes begin
        """
        # Figure out the operands details for the RISC-Stack ISA
        if self.isa == "risc1":
            pass

        # Figure out the operands details for the RISC-Accumulator ISA
        if self.isa == "risc2":
            pass

        # Figure out the operands details for the RISC-Register ISA
        if self.isa == "risc3":

            # Load the special case moves for RISC-Register architecture
            low_high_load_risc = ["mov_low", "mov_high"]
            low_high_load_risc = [bitarray(code) for code in self.instructions_dict if
                                  self.instructions_dict[code][0] in low_high_load_risc]

            # Load low/high bytes check for RISC-register architecture
            if self.opcode in low_high_load_risc:
                start_point = 5
            else:
                start_point = 6

        # Figure out the operands details for the CISC-Register ISA
        if self.isa == "cisc":
            pass

        return start_point

    def __determine_result_dest(self, start_point, operands_aliases):
        """
        Determines where to save the result and whether the memory is going to be affected
        :param start_point: the point in the instruction where operands' encodings start
        :param operands_aliases: list of aliases for the operands encoded in binary
        """
        # Set 'write' access to the memory to False by default
        memory_write_access = False
        result_destination = None

        # Determining where to save the result of the operation depending on type of the operation specified
        # If the result is saved in the first operand
        if (res_type := self.instructions_dict[self.opcode.to01()][1]) == "firstop":

            if operands_aliases[0] == "reg":
                # If the destination is the register
                register_code = self.instruction[start_point:start_point + 3].to01()
                result_destination = self.register_codes[register_code]

            elif operands_aliases[0] == "memreg":
                # If the destination is memory
                memory_write_access = True
                register_code = self.instruction[start_point:start_point + 3].to01()
                result_destination = int(self.register_codes[register_code]._state.to01(), 2)

        # If the result is popped from the stack
        elif res_type == "stackpop":
            register_code = self.instruction[start_point:start_point + 3].to01()
            result_destination = self.register_codes[register_code]

        # If the result is the flag register affected (compare ops)
        elif res_type == "flags":
            result_destination = self.registers["FR"]

        # If the result is outputted to a device, we should output to the specified port
        elif res_type == "out":

            if self.io_arch == "mmio":
                raise SimulatorError("This instruction does not exist in MMIO architecture")
            else:
                imm_len = int(operands_aliases[0][3:])
                port_num = int(self.instruction[start_point:start_point + imm_len].to01(), 2)
                result_destination = self.ports_dictionary[str(port_num)]

        return memory_write_access, result_destination

    def __push_stack(self, value):
        """
        Pushes the value onto the memory stack, changing the position of the Stack Pointer register
        :param value: bitarray(16) - a value to be pushed into memory
        """
        stack_pointer_value = int(self.registers["SP"]._state.to01(), 2)
        self.data_memory.write(stack_pointer_value, value)
        self.registers["SP"]._state = bitarray(bin(stack_pointer_value + 2)[2:].rjust(16, '0'))

    def __pop_stack(self):
        """
        Pops the last value from the memory stack, changing the position of the Stack Pointer register
        :return: bitarray - of size 16 representing the value of the register previously pushed onto the stack
        """
        stack_pointer_value = int(self.registers["SP"]._state.to01(), 2)
        self.registers["SP"]._state = bitarray(bin(stack_pointer_value - 2)[2:].rjust(16, '0'))
        return self.data_memory.read_data(stack_pointer_value - 2, stack_pointer_value)

    # Below are the methods for curses-driven command-line interface
    # TODO: Create a basic API of data we need to transmit for the web interface to work properly
    #  A somewhat later goal, sure, but still
    def curses_next_instruction(self):
        """
        A temporary module that switches to the next instruction when curses mode is on
        """
        while True:
            key = self.instruction_window.getkey()
            # Move on to the next instruction if the 'n' key is pressed
            if key in ('N', 'n'):
                logger.info("N pressed")
                return False
            # Finish the program if the 'q' key is pressed
            if key in ('Q', 'q'):
                logger.info("Q pressed")
                return True

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

        if self.architecture in ["neumann", "harvardm"]:
            # Create the box for the memory representation
            self.data_memory_window = curses.newwin(19, 130, 10, 2)
            self.data_memory_window.box()
            # Create the window for the memory print
            self.data_memory_box = self.data_memory_window.subwin(17, 128, 11, 3)
        else:
            # Create the boxes for the data and program memory representation
            self.data_memory_window = curses.newwin(19, 130, 10, 2)
            self.program_memory_window = curses.newwin(19, 130, 30, 2)
            self.data_memory_window.box()
            self.program_memory_window.box()
            # Create the windows for the data and program memory print
            self.data_memory_box = self.data_memory_window.subwin(17, 128, 11, 3)
            self.program_memory_box = self.program_memory_window.subwin(17, 128, 31, 3)

        # Create the box for the shell representation
        self.shell_window = curses.newwin(3, 23, 2, 60)
        self.shell_window.box()
        self.shell_box = self.shell_window.subwin(1, 21, 3, 61)

        # Refresh all the internal datastructures bottom-up, update the screen
        self.std_screen.noutrefresh()
        self.instruction_window.noutrefresh()
        self.register_window.noutrefresh()
        self.data_memory_window.noutrefresh()
        self.shell_window.noutrefresh()
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
        self.instruction_box.addstr(self.instructions_dict[self.opcode.to01()][0])

        # Fill the register box with current registers and their values
        self.register_box.clear()
        self.register_box.addstr(" Registers:\n")
        items = [(value.name, value._state.tobytes().hex()) for key, value in self.registers.items()]
        for i in range(1, len(items), 2):
            self.register_box.addstr(f" {(items[i - 1][0] + ':').ljust(4, ' ')} {items[i - 1][1]}  "
                                     f"{(items[i][0] + ':').ljust(4, ' ')} {items[i][1]}\n")

        # Refresh the data memory on screen
        self.data_memory_box.clear()
        for i in range(0, len(self.data_memory.slots), 8):
            self.data_memory_box.addstr(ba2hex(self.data_memory.slots[i:i + 8]))

        # If the architecture has two separate memories, we update the program memory too
        if self.architecture == "harvard":
            self.program_memory_box.clear()
            for i in range(0, len(self.program_memory.slots), 8):
                self.program_memory_box.addstr(ba2hex(self.program_memory.slots[i:i + 8]))

        # Refresh the shell output
        self.shell_box.clear()
        for port, device in self.ports_dictionary.items():
            self.shell_box.addstr(str(device))

        # Refreshing the contents of screen elements and updating the whole screen
        self.std_screen.noutrefresh()
        self.instruction_box.noutrefresh()
        self.register_box.noutrefresh()
        self.data_memory_box.noutrefresh()
        self.shell_box.noutrefresh()
        curses.doupdate()

    def close_screen(self):
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
