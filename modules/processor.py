#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0

# This is the main module of the Hardware Simulator that processes binary instructions

#     Emulates the work of a real computer with:
#         * 64kib memory (in the future, now it's just 1kib)
#         * processor registers
#
#     Is supposed to handle a few ISA architectures:
#         * Stack
#         * Accumulator
#         * RISC Register
#         * CISC Register architectures
#
#     As well as having a switch between:
#         * Memory-Mapped Input/Output
#         * Separate space Input/Output (Special instructions really)
#
#     Has a switch as well to include SIMD instructions (only for CISC)
#
#     Supports a few computer architectures as well:
#         * von Neumann
#         * Harvard
#         * Harvard modified

# Basic workflow of the CPU is as follows:
#   * Create the registers, memory according to the architectures specified
#   * Load the program binary code into memory at starting position (IP)
#   * Then, the CPU executes instructions one by one, whether by manual presses, or at certain time intervals,
#         everything is controlled by web_next_instruction call, it skips to the next instructions, executing it,
#         and updates everything attached to CPU (Should not be called immediately after the last call,
#         processing might take some time)
#   * Instruction execution involves several steps as well:
#       * First, we decode the actual instruction part of it (opcode), determining which operands we are
#           going to meet and other details on it
#       * Second, we determine where to save the result (it might be a register, memory slot, or the result might
#           not need to be saved at all, like in jump instructions)
#       * Then, we encode or decode the operands, collecting their values
#       * As a last step, we actually determine what is the computation that this instruction needs,
#           and either call a function from functions_dict submodule, or process the stuff on our own

# Conventions on anything pointing to the memory, including:
#   * Instruction Pointer
#   * Stack Pointer
#   * TOS
#   * Index register
#     etc.
# UPDATE: Instruction Pointer works with bytes, and thus can point up to 64KiB of 8-bit
# (or 6-bit, depending on the architecture) bytes
#
# Other ones work with bytes too (SP, TOS, IR), but they are always 8-bits, and operate mainly on 16-bit words
# read_data works with bits
# write_data works with bits
#
# Current standard values of these pointers are:
# self.ip_start - Instruction Pointer = 512 byte
# (Start point for program loading, Grows incrementing, Shrinks decrementing)
#
# self.tos_start - Top Of the Register Stack (TOS) = 256 byte
# (Grows incrementing, Shrinks decrementing)
#
# self.stack_start - Regular Stack = 65536 (last) byte  (for now it's 1024)
# (Grows decrementing, Shrinks incrementing)

# TODO: This module needs a lot of refactoring (after the available demo working properly), as
#  it still has a lot of leftover curses functionality we are not going to need anymore,
#  overall does not perform ideally, as it was made up on the go

# TODO: Additionally, we do not use the general-purposiveness info provided to us by register module,
#  and the user is currently free to do whatever they want with any register, defying the purpose
#  of the special registers (SP, IP, FR etc.). This is probably going to be done after a massive refactoring/remake

# TODO: Plus, we probably do not need any distinction between registers and memory, as memory can be
#  really just a huge general-purpose register, or the other way around, whatever

# TODO: Implement 'add carry' and similar operations for RISC2, RISC3 architectures

import os
import json
import curses
import logging
from bitarray import bitarray
from bitarray.util import ba2hex

from modules.functions import functions_dictionary, twos_complement
from modules.memory import Memory
from modules.register import Register
from modules.shell import Shell


class CPU:
    """
    Class for CPU representation
    Actually handles the program logic
    Provides all arithmetics and memory manipulations
    """

    def __init__(self, isa, architecture, io_arch, program_text, program_start=512, curses_mode=False, debug_mode=True):
        """
        Creates a new CPU.
        :param isa: chosen ISA
        :param architecture: chosen Architecture type
        :param io_arch: chosen Input/Output type
        :param program_text: str - text of the binary program file
        :param program_start: location in the memory for the program code, as an offset from default
        :param curses_mode: bool - representing whether the app should draw curses interface or not
        :param debug_mode: bool - representing whether to log the information or not
        :return: NoneType
        """
        self.isa = isa
        self.architecture = architecture
        self.io_arch = io_arch
        self.curses_mode = curses_mode
        self.instruction = bitarray('')

        # Set up the logging module so it would save everything to a file
        # (we are unable to track prints in real-time due to curses)
        logging.basicConfig(filename="log.txt",
                            filemode='w',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

        self.logger = logging.getLogger('processor')

        # Disables the logger if we are not in debug mode
        if not debug_mode:
            self.logger.disabled = True

        self.logger.debug(f"Created new CPU instance (ISA: {self.isa}, Architecture: {self.architecture}, "
                          f"I/O: {self.io_arch}, CursesMode: {self.curses_mode})")

        self.memory_size = 1024
        # Create data and program memory according to the specified architecture
        if architecture in ["neumann", "harvardm"]:
            memory = Memory(self.memory_size)
            self.data_memory = memory
            self.program_memory = memory
        elif architecture == "harvard":
            self.data_memory = Memory(self.memory_size)
            self.program_memory = Memory(self.memory_size)

        # Create the registers for the specified register architecture
        self.__create_registers()

        # Create devices for this CPU depending on the I/O architecture specified
        if io_arch == "mmio":
            shell = Shell(io_arch, start=1004, end=1024)
        else:
            shell = Shell(io_arch)
        self.ports_dictionary = {"1": shell}

        # Opening the instruction set and choosing the one for our chosen ISA architecture
        with open(os.path.join("modules", "instructions.json"), "r") as file:
            self.instructions_dict = json.load(file)[self.isa]

        # Determining the size of the instructions to read (size of the instruction, opcode size, byte size)
        instruction_sizes = {"risc1": (6, 6, 6), "risc2": (8, 8, 8), "risc3": (16, 6, 8), "cisc": (8, 8, 8)}
        self.instruction_size = instruction_sizes[self.isa]

        # Set the instruction pointer to the starting point of the program and load the specified program into memory
        self.registers["IP"].write_data(bin(program_start)[2:])
        self.__load_program(program_text)
        self.read_state = "opcode"
        self.first_instruction = True
        self.is_input_active = False

        self.instruction = bitarray('')

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

        # Create registers, work on special cases
        for register in registers_list:
            temp = Register(register[0], general_purpose=(register[1] == 1))

            # Remember the starting point of the 'register stack' or 'memory stack'
            if register[0] == "TOS":
                self.tos_start = 256
                temp.write_data(bin(self.tos_start)[2:])
            elif register[0] == "SP":
                self.stack_start = 1024
                temp.write_data(bin(self.stack_start)[2:])

            self.registers[register[0]] = temp
            self.register_codes[register[2]] = temp

        self.logger.debug(f"Created registers: {', '.join([register[0] for register in registers_list])}")

    def __load_program(self, program_text):
        """
        Loads the program into memory at Instruction Pointer
        :param program_text: str - text of the binary program file
        """
        # Writing program instructions into to memory
        ip_value = int(self.registers["IP"]._state.to01(), 2)
        self.program_memory.write_data(ip_value * self.instruction_size[2], bitarray(program_text.replace('\n', '')))

        # Determine the number of bytes for each instruction, and start at the beginning of the program (0th index)
        self.instr_size_list = list(map(lambda x: len(x) // self.instruction_size[2], program_text.split('\n')))
        self.program_pointer = 0
        self.logger.debug(f"Program was loaded into program memory starting at {ip_value} byte")
        self.logger.debug(f"Instruction size list: {self.instr_size_list}")

    def web_next_instruction(self):
        """
        Executes the next instruction after button click on the webpage
        Only starts executing AFTER the first call, only reads the instruction on the first time
        """
        self.logger.debug("Next instruction is executing")
        # If the instruction is 'end' - an empty string, terminate the execution
        if isinstance(self.instruction, bitarray) and self.instruction.to01() == ('0' * self.instruction_size[0]):
            self.logger.debug("Next instruction is 'end' instruction")
            return

        # If we are still waiting for input, we can't execute the next instruction
        if self.is_input_active:
            self.logger.debug("Can't execute next instruction, CPU waits for the input")
            return

        if self.first_instruction:
            self.first_instruction = False
        else:
            # Execute the cycle
            self.__execute_cycle()

            # Update the Memory-Mapped devices
            self.__update_devices()

        # Read first instruction of the program from the memory
        self.__read_instruction()

    def __read_instruction(self):
        """
        Reads the instruction and the opcode in it for a specified ISA
        Reads a long immediate encoded in the next byets if the ISA uses those
        Does not actually move the instruction pointer to the next instruction
        """
        start_read_location = int(self.registers["IP"]._state.to01(), 2) * self.instruction_size[2]
        self.instruction = self.program_memory.read_data(start_read_location,
                                                         start_read_location + self.instruction_size[0])

        # Read the opcode part of the instruction
        if self.read_state == "opcode":
            self.opcode = self.instruction[0:self.instruction_size[1]]

            # If the first bit of the encoded binary instruction indicates that the next two
            # bytes are going to be an immediate constant, change the read_state
            if self.isa in ["risc1", "risc2"] and self.opcode[0]:
                self.read_state = "constant"
            self.additional_jump = 0

        printout_temp = f"READ: Instruction: {self.instruction.to01()}, Opcode: {self.opcode.to01()}"

        # If we are in the state of reading the two-byte encoded immediate constant,
        # read it and add to the list of operands
        if self.read_state == "constant":
            self.long_immediate = self.program_memory.read_data(start_read_location + 1 * self.instruction_size[2],
                                                                start_read_location + 3 * self.instruction_size[2])

            # In order to turn 12-bit signed number into 16-bit signed number, we copy the sign bit into all high bits
            self.long_immediate = bitarray(self.long_immediate.to01().rjust(16, self.long_immediate.to01()[0]))
            self.additional_jump = 2
            self.read_state = "opcode"
            printout_temp += f", Long immediate constant: {self.long_immediate.to01()}"

        self.logger.debug(printout_temp)

    def __execute_cycle(self):
        """
        Execute the current instruction, and move on to the next one, moving the instruction pointer
        """
        is_close = False
        # Waiting for the key or button to be pressed, depending on the mode
        if self.curses_mode:
            is_close = self.curses_next_instruction()

        # Executing the instruction if it's not a 'nop' - no operation instruction
        # TODO: Possibly get rid of 'end' instruction, substituting them with nops
        if (instr_name := self.instructions_dict[self.opcode.to01()][0]) == "nop":
            self.logger.debug('NOP OPERATION')
            go_to_next_instruction = True
        else:
            go_to_next_instruction = self.execute()

        self.logger.debug("FINISH decoding and executing the instruction")
        registers_state = ', '.join([f'{name}: {ba2hex(register._state)}' for name, register in self.registers.items()])
        self.logger.debug(F"Registers state: {registers_state}")
        if go_to_next_instruction:
            ip_val = int(self.registers["IP"]._state.to01(), 2)
            bytes_per_instruction = self.instruction_size[0] // self.instruction_size[2]
            ip_val = bin(ip_val + bytes_per_instruction + self.additional_jump)[2:]
            self.program_pointer += 1
            self.registers["IP"].write_data(ip_val)
            self.logger.debug("MOVE IP to the next instruction")

        self.logger.debug("-" * 100)
        return is_close

    def __update_devices(self):
        """
        Updates the devices if they are Memory-Mapped
        """
        for port, device in self.ports_dictionary.items():
            if device.io_type == "mmio":
                self.logger.debug(f"Updating mmio device at {port}, memory[{device.start_point}:{device.end_point}]")
                data = self.data_memory.read_data(device.start_point * 8, device.end_point * 8)
                device._state = data

    def execute(self):
        """
        Executes an instruction, decoding its operands, computing the
        result and saving it in the proper place
        :return: bool - whether to go to the next instruction
        """
        self.logger.debug("START decoding and executing the instruction")
        # The return value that tells whether we should go to the next instruction after the execution
        go_to_next_instruction = True

        # Determine the point in the binary instruction where operands start
        start_point = self.__determine_start_point()

        # Reading the list of operands encoded in the binary instruction
        if self.isa in ["risc3", "cisc"]:
            operands_aliases = self.instructions_dict[self.opcode.to01()][-1]
        else:
            operands_aliases = self.instructions_dict[self.opcode.to01()][1][1:]
        self.logger.debug(f"INST INFO, <{self.instructions_dict[self.opcode.to01()][0]}> "
                          f"Operands Aliases: {operands_aliases}")

        # Get the values of the operands for this function
        operands_values = self.__add_operands(start_point, operands_aliases)
        self.logger.debug(f"INST INFO Operands Values: {operands_values}")

        # Determine whether the memory is going to be affected as a
        # result of the operation and where to save it
        memory_write_access, result_destination, tos_push = self.__determine_result_dest(start_point, operands_aliases)
        self.logger.debug(f"INST INFO (Memory Write Access: {memory_write_access}, "
                          f"Destination: {result_destination}, TOS_Push: {tos_push})")

        # Different architectures have different kinds of instructions encodings
        if self.isa in ["risc3", "cisc"]:
            res_type = self.instructions_dict[self.opcode.to01()][1]
        else:
            res_type = self.instructions_dict[self.opcode.to01()][1][0]

        # If the opcode type is call, we can perform the needed actions without calling functions_dict
        if res_type == "call":

            # Remember the next instruction after the one which called the 'call' function
            next_instruction = self.program_pointer + 1
            if self.isa == "risc3":
                self.registers["LR"].write_data(bin(next_instruction)[2:])
            else:
                self.__push_stack(bitarray(bin(next_instruction)[2:].rjust(16, '0')))

            # There is only one operand for a call function, and it determines the program_start from the IP
            operand = operands_aliases[0]
            if operand.startswith("imm"):
                if self.isa in ["risc3", "cisc"]:
                    # Calculate the new location of the instruction pointer, change it
                    imm_len = int(operand[3:])
                    jump_num = twos_complement(int(operands_values[0].to01(), 2), imm_len)
                else:
                    jump_num = twos_complement(int(self.long_immediate.to01(), 2), self.instruction_size[0] * 2)
            elif operand == "reg":
                jump_num = twos_complement(int(operands_values[0].to01(), 2), 16)

            # Calculate the new program_start in instructions
            if jump_num >= 0:
                jump_distance = sum(self.instr_size_list[self.program_pointer:self.program_pointer + jump_num])
            else:
                jump_distance = -1 * sum(self.instr_size_list[self.program_pointer + jump_num:self.program_pointer])

            # Change the instruction pointer
            ip_value = int(self.registers["IP"]._state.to01(), 2)
            self.registers["IP"].write_data(bin(ip_value + jump_distance)[2:])
            self.program_pointer += jump_num
            self.logger.debug(f"INST INFO: <call> (Distance: {jump_num}, Bytes: {jump_distance}, "
                              f"Bits: {jump_distance * self.instruction_size[2]})")

            go_to_next_instruction = False

        # If the opcode type is return, we just move the instruction pointer back
        elif res_type == "ret":

            # TODO: Should we zero out the Link Register register after returning to it once?
            # In RISC-Register architecture we retrieve the caller address in the Link Register,
            # otherwise we just pop it on the stack
            if self.isa == "risc3":
                return_point = int(self.registers["LR"]._state.to01(), 2)
            else:
                return_point = self.__pop_stack()

            ip_value = int(self.registers["IP"]._state.to01(), 2)
            if self.program_pointer >= return_point:
                destination = ip_value - sum(self.instr_size_list[return_point:self.program_pointer])
            else:
                destination = ip_value - sum(self.instr_size_list[self.program_pointer:return_point])

            self.registers["IP"].write_data(bin(destination)[2:])
            self.program_pointer = return_point
            go_to_next_instruction = False
            self.logger.debug(f"INST INFO <ret> (Return Point {return_point}, Program Pointer {self.program_pointer})")

        # If the opcode is of type jump, we look at the Flag Register and move Instruction Pointer if needed
        elif res_type == "jmp":

            # Set jump by default to False
            should_jump = False
            flag_reg = self.registers["FR"]._state
            carry_flag, zero_flag, overflow_flag, sign_flag = flag_reg[-4:]

            # Check the needed flags according to the jump condition specified
            if (jmp_spec := self.instructions_dict[self.opcode.to01()][0]) == "jmp":
                should_jump = True
            elif jmp_spec == "jc":
                if operands_values[0] == bitarray("1" * 16):
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
                should_jump = (sign_flag != overflow_flag) or zero_flag

            # If the jump condition was satisfied, jump to the value specified with the operand
            if should_jump:

                # If the program_start was specified with the number, its length was specified as well
                # Else, just use the register length or long immediate length
                if operands_aliases[0].startswith("imm") and self.isa in ["risc3", "cisc"]:
                    num_len = int(operands_aliases[0][3:])
                else:
                    num_len = 16

                # Calculate the new program_start in instructions
                if self.isa in ["risc3", "cisc"]:
                    jump_num = twos_complement(int(operands_values[0].to01(), 2), num_len)
                else:
                    jump_num = twos_complement(int(self.long_immediate.to01(), 2), num_len)

                # Calculate the number of bits to jump
                if jump_num >= 0:
                    jump_distance = sum(self.instr_size_list[self.program_pointer:self.program_pointer + jump_num])
                else:
                    jump_distance = -1 * sum(self.instr_size_list[self.program_pointer + jump_num:self.program_pointer])

                # Change the instruction pointer
                self.logger.debug(f"INST INFO <jmp> (Distance: {jump_num}, Bytes: {jump_distance}, "
                                  f"Bits: {jump_distance * self.instruction_size[2]})")
                ip_value = int(self.registers["IP"]._state.to01(), 2)
                self.registers["IP"].write_data(bin(ip_value + jump_distance)[2:])
                self.program_pointer += jump_num
                go_to_next_instruction = False
            else:
                self.logger.debug("INST INFO <jmp> not successful")

        # If the opcode specified pushes the value on the stack
        elif res_type == "stackpush":
            self.logger.debug(f"INST INFO <stackpush>")
            self.__push_stack(operands_values[0])

        # If the opcode specified pops the value from the stack into the register
        elif res_type in ["stackpop", "stackpopf"]:
            popped_val = self.__pop_stack()
            if memory_write_access:
                self.data_memory.write_data(result_destination // 8, popped_val)
                if tos_push:
                    self.registers["TOS"].write_data(bin(result_destination + 2)[2:])
            else:
                result_destination.write_data(popped_val)
            self.logger.debug(f"INST INFO <stackpop> (Popped value {ba2hex(popped_val)}, )")

        # If the opcode specifies outputting to the device
        elif res_type == "out":
            self.logger.debug(f"INST INFO outputting to the device {operands_values[-1]}")
            result_destination.out_shell(operands_values[-1])

        # If we are getting input from device, we 'hang' the processor so that it waits for input
        elif res_type == "in":
            self.logger.debug("INST INFO CPU is waiting for the input from the device")
            self.is_input_active = True
            self.input_result_destination = result_destination
            # TODO: Currently, the port: device interface is not ideal, and is not finished,
            #  one of the places we will need to fix for it to work is input instructions, as they
            #  currently assume just one device to receive input from, which is not great

        # Swapping two of the top TOS values
        elif res_type == "swap":
            self.logger.debug("INST INFO Swapping TOS")
            self.data_memory.write_data(result_destination * 8, operands_values[0])
            self.data_memory.write_data(result_destination * 8 + 16, operands_values[1])
            self.registers["TOS"].write_data(bin(result_destination + 4)[2:])

        # Else, we have to execute the needed computations for this function in the virtual ALU
        else:
            # Determine the needed function for this opcode and execute it, passing the flag register
            function = functions_dictionary[self.instructions_dict[self.opcode.to01()][0]]
            result_value = function(operands_values, flag_register=self.registers["FR"])

            # Write the result of the operation into the memory
            if memory_write_access:
                self.data_memory.write_data(result_destination * 8, result_value)

                # Move the TOS pointer if the instruction pushed into the virtual register stack
                if tos_push:
                    self.registers["TOS"].write_data(bin(result_destination + 2)[2:])

            # Write into the result destination
            else:
                result_destination.write_data(result_value)

        return go_to_next_instruction

    def __determine_start_point(self):
        """
        Determines the start point of the operands in the instruction and other details
        depending on the ISA architecture

        The helper function for the 'execute' method

        :return: start_point - int, representing the bit value in the instruction from which the opcodes begin
        """
        # Figure out the operands details for the RISC-Stack ISA
        if self.isa in ["risc1", "risc2"]:
            start_point = None

        # Figure out the operands details for the RISC-Register ISA
        elif self.isa == "risc3":

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
        else:
            start_point = 8

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
        tos_push = False

        # Determining where to save the result of the operation depending on type of the operation specified
        #
        # RISC-Stack ISA
        if self.isa == "risc1":

            # Determining the result destination for RISC-Stack iSA
            if (res_type := self.instructions_dict[self.opcode.to01()][1][0]) in ["tos", "in", "swap"]:
                memory_write_access, tos_push = True, True
                result_destination = int(self.registers["TOS"]._state.to01(), 2)
            elif res_type == "memtos":
                memory_write_access = True
                tos_val = int(self.registers["TOS"]._state.to01(), 2) * 8
                result_destination = int(self.data_memory.read_data(tos_val, tos_val + 16).to01(), 2)
            elif res_type == "fr":
                result_destination = self.registers["FR"]
            elif res_type == "stackpop":
                memory_write_access, tos_push = True, True
                result_destination = int(self.registers["TOS"]._state.to01(), 2)
            elif res_type == "stackpopf":
                result_destination = self.registers["FR"]
            elif res_type == "out":
                result_destination = self.ports_dictionary[str(int(self.long_immediate.to01(), 2))]

        # Accumulator-RISC
        elif self.isa == "risc2":

            # Determining the result destination for RISC-Accumulator ISA
            if (res_type := self.instructions_dict[self.opcode.to01()][1][0]) in ["acc", "in", "stackpop"]:
                result_destination = self.registers["ACC"]
            elif res_type == "memir":
                memory_write_access = True
                result_destination = int(self.registers["IR"]._state.to01(), 2)

        # Register-RISC and CISC architectures
        elif self.isa in ["risc3", "cisc"]:

            # If the result is to be saved into the first operand
            if (res_type := self.instructions_dict[self.opcode.to01()][1]) in ["firstop", "in"]:

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

        return memory_write_access, result_destination, tos_push

    def __add_operands(self, start_point, operands_aliases):
        """
        Adds operands values to the list to provide to a chosen function later
        :param operands_aliases: list of short instruction type strings
        :return: operands_values - list of binary data for the functions to compute on
        """
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
                tmp_register = twos_complement(int(self.register_codes[register_code]._state.to01(), 2), 16) * 8
                operands_values.append(self.data_memory.read_data(tmp_register, tmp_register + 16))
                start_point += 3

            # If the operand is the immediate constant, add its value and go to the next operand
            elif operand.startswith("imm"):
                if self.isa in ["risc1", "risc2"]:
                    operands_values.append(self.long_immediate)
                else:
                    immediate_length = int(operand[3:])
                    operands_values.append(bitarray(self.instruction[start_point:start_point + immediate_length]))
                    start_point += immediate_length

            elif operand == "tos":
                operands_values.append(self.__pop_tos())

            elif operand == "tospop":
                operands_values.append(self.__pop_tos(pop=True))

            elif operand == "tos2":
                operands_values.append(self.__pop_tos(second=True))

            elif operand == "memtos":
                tos_value = int(self.__pop_tos(pop=True).to01(), 2) * 8
                operands_values.append(self.data_memory.read_data(tos_value, tos_value + 16))

            elif operand == "memir":
                ir_value = int(self.registers["IR"]._state.to01(), 2) * 8
                operands_values.append(self.data_memory.read_data(ir_value, ir_value + 16))

            elif operand == "memimm":
                start_read = int(self.long_immediate.to01(), 2) * 8
                operands_values.append(self.data_memory.read_data(start_read, start_read + 16))

            elif operand in ["fr", "ir", "acc"]:
                operands_values.append(self.registers[operand.upper()]._state)

            elif operand == "one":
                operands_values.append(bitarray(bin(1)[2:].rjust(16, '0')))

        return operands_values

    def __push_stack(self, value):
        """
        Pushes the value onto the memory stack, changing the position of the Stack Pointer register
        :param value: bitarray(16) - a value to be pushed into memory
        """
        stack_pointer_value = int(self.registers["SP"]._state.to01(), 2) * 8
        self.data_memory.write_data(stack_pointer_value - 16, value)
        self.registers["SP"]._state = bitarray(bin(stack_pointer_value // 8 - 2)[2:].rjust(16, '0'))
        self.logger.debug(f"Push to stack: {ba2hex(value)}")

    def __pop_stack(self):
        """
        Pops the last value from the memory stack, changing the position of the Stack Pointer register
        :return: bitarray - of size 16 representing the value of the register previously pushed onto the stack
        """
        stack_pointer_value = int(self.registers["SP"]._state.to01(), 2) * 8
        self.registers["SP"].write_data(bin(stack_pointer_value // 8 + 2)[2:])
        self.logger.debug(f"Pop from stack: {ba2hex(self.registers['SP']._state)}")
        return self.data_memory.read_data(stack_pointer_value, stack_pointer_value + 16)

    def __pop_tos(self, second=False, pop=False):
        """
        Gets the value of the 'tos', which lies in memory, and moves the register stack if needed
        :param second: bool - whether to return the value of the second-to-top register
        :param pop: bool - whether to move the stack behind the popped value
        """
        start_read = int(self.registers["TOS"]._state.to01(), 2) * 8
        tos_val = start_read
        if second and start_read > self.tos_start:
            start_read -= 16
        return_data = self.data_memory.read_data(start_read - 16, start_read)
        if pop:
            self.registers["TOS"].write_data(bin(tos_val // 8 - 2)[2:])
        self.logger.debug(f"Pop from TOS stack: (newtosval: {ba2hex(self.registers['TOS']._state)}, "
                          f"second: {second}, pop: {pop})")
        return return_data

    def input_finish(self, char):
        """
        Stops the waiting process for the CPU, putting the result of the operation in a register specified
        :param char: bitarray of size 16, the result of the input
        """
        self.is_input_active = False
        self.input_result_destination.write_data(char)

    # Below are the methods for curses-driven command-line interface
    def start_program(self):
        """
        Handles the execution of the actual program for a curses-based application
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
                self.draw_screen()

            if self.instruction.to01() == ('0' * self.instruction_size[0]):
                return False

            is_close = self.__execute_cycle()
            if is_close:
                return True

    def curses_next_instruction(self):
        """
        A temporary module that switches to the next instruction when curses mode is on
        """
        while True:
            key = self.instruction_window.getkey()
            # Move on to the next instruction if the 'n' key is pressed
            if key in ('N', 'n'):
                return False
            # Finish the program if the 'q' key is pressed
            if key in ('Q', 'q'):
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
