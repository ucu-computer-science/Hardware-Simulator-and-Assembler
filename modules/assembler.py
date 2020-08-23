#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0

# TODO: Implement label decoding for jumps and calls

# TODO: Implement assembly directives (db and dw)

# TODO: There is more though, instructions.json is pretty inconsistent between different
#  architectures as it was all done on the go, and is under-documented


import os
import json
import argparse
from collections import defaultdict

from modules.functions import twos_complement


class AssemblerCLI:
    """
    Command-Line interface for the Assembler (as opposed to the general functionality class)
    """

    def __init__(self):
        """
        Checks the validity of the arguments and instantiates new Assembler class instance with them
        """
        # Creating the command line parser and main arguments
        parser = argparse.ArgumentParser()
        parser.add_argument("-f", "--file", help="provide the assembly program filepath")
        parser.add_argument("--isa", help="specify the ISA architecture: RISC1 (Stack), "
                                          "RISC2 (Accumulator), RISC3 (Register), CISC (Register)")
        parser.add_argument("-o", "--output", help="Specify the output file")

        # Parsing the command line arguments
        args = parser.parse_args()

        # Check if the assembly program file was provided
        if not args.file:
            raise AssemblerError("Assembly program filepath not provided")

        # Check if the ISA is provided and actually exists
        valid_isa = ['risc1', 'risc2', 'risc3', 'cisc']
        if not args.isa or args.isa.lower() not in valid_isa:
            raise AssemblerError("Specify the valid instruction set architecture")

        # Read the program text
        with open(args.file, "r") as file:
            program_text = file.read()

        binary_program = Assembler(args.isa.lower(), program_text).binary_code

        # If there was an output path provided, save the binary code there
        if args.output:
            output_path = args.output

        # If there was no output path provided, save the binary code in the
        # same folder as the assembly program with a different file extension
        else:
            output_path = os.path.join(os.path.dirname(args.file),
                                       os.path.splitext(os.path.basename(args.file))[0] + ".bin")

        with open(output_path, "w") as file:
            file.write(binary_program)


class Assembler:
    """
    Assembler class. Takes a file and specified architecture type as
    an input, and translates to binary code
    """

    def __init__(self, isa, program_text):
        """
        Initializes the assembler, outputs the binary code file
        The actual encoded binary text is in self.binary_code
        """
        self.isa = isa

        # Open the list of instructions for this architecture and reformat it for our purposes
        # DefaultDict allows to have several values for the same key all pushed into type specified - we use list
        # This is useful since we might have the same assembly instruction encoded differently depending on the operands
        with open(os.path.join("modules", "instructions.json"), "r") as file:
            self.instructions = defaultdict(list)
            for opcode, details in json.load(file)[isa].items():
                self.instructions[details[0]].append([opcode, details[-1]])

        # Open the list of registers for this architecture and format it properly
        with open(os.path.join("modules", "registers.json"), "r") as file:
            registers = json.load(file)[isa]
            self.register_names = {register[0]: register[2] for register in registers}

        # Determining the size of the instructions to read
        instruction_sizes = {"risc1": (6, 6), "risc2": (8, 8), "risc3": (16, 6), "cisc": (8, 8)}
        self.instruction_size = instruction_sizes[isa]

        self.binary_code = self.translate(program_text)

    def translate(self, text):
        """
        Translates the assembly code into binary code
        :param text: str - assembly code
        """
        # TODO: Possible consideration of assembly using regex pattern matching,
        #  we are basically doing almost that already
        #  This would eliminate the need to check the validity of the operands separately,
        #  as they are going to be a part of the pattern. Can be precompiled and is super fast too
        #  We basically won't need registers dict for decoding part of the assembly,
        #  but still will need that for the actual translation and decoding processes
        binary_code = ""

        # Divide the program into lines
        for line in text.split("\n"):
            line = line.rstrip(" ")
            # Check if its an empty line or a comment line, skip if yes
            if line.strip(" ").startswith("#") or line.isspace() or not line:
                continue
            self.line = line

            # Split instruction name and operands
            binary_line = ""
            arguments = line.split(" ")
            assembly_instruction, operands = arguments[0], arguments[1:]

            for ind, operand in enumerate(operands[:-1]):
                if not operand.endswith(','):
                    raise AssemblerError(f"Provide valid operands for this instruction (commas included): {line}")
                operands[ind] = operand[:-1]

            # Check if the instruction actually exists for this architecture
            if assembly_instruction not in self.instructions:
                raise AssemblerError(f"Not valid assembly instruction: {assembly_instruction}")

            # Get the list of encodings for this assembly instruction
            instructions_info = self.instructions[assembly_instruction]

            # If this assembly instruction has only one encoding, encode it and its operands
            if len(instructions_info) == 1:
                binary_line = self.__encode_operands(operands, instructions_info[0])
            else:

                # If this assembly instruction has a few different opcodes depending on the type of operands
                # we check every possible option until we find the one we needed
                for instruction_info in instructions_info:
                    try:

                        # Low and High byte moves have 5-bit opcodes, a special case
                        if assembly_instruction in ["mov_low", "mov_high"] and len(instruction_info[0]) != 5:
                            instruction_info[0] = instruction_info[0][:-1]

                        binary_line = self.__encode_operands(operands, instruction_info)
                        break
                    except AssemblerError:
                        continue

                # If all of the opcode options were wrong, raise the error
                if not binary_line:
                    raise AssemblerError(f"Provide valid operands for this instruction: {line}")

            binary_code += binary_line + "\n"

        return binary_code

    def __encode_operands(self, operands, instruction_info):
        """
        Encodes the operands given an opcode and operands types
        :param operands: list - list of operands-strings
        :param instruction_info: list - of instruction encoding and operand types
        """
        binary_line = instruction_info[0]
        types = instruction_info[1]

        # Eliminate processor-only information in type lists
        if "one" in types: types.remove("one")

        instruction_length = self.instruction_size[0]
        if self.isa == "cisc":
            register_byte = ""
            immediate_bytes = ""

        if len(operands) != len(types):
            raise AssemblerError(f"Provide valid operands for this instruction: {self.line}")

        # TODO: This probably could be moved to a separate function to allow for normal recursion calls
        # TODO: Offsets work only like this for now: [%reg + $-5], implement proper workflow for [%reg - $5]

        # Check if the operand provided is of the type needed, if yes, encode and add it to the current line
        for index, operand in enumerate(operands):
            if self.__valid_type(operand, op_type := types[index]):

                # Encode the operand properly and add it to the line
                if op_type == "reg" or op_type == "fr":
                    if self.isa == "cisc":
                        register_byte += self.register_names[operand[1:]]
                    else:
                        binary_line += self.register_names[operand[1:]]

                elif op_type == "regoff":
                    index = operand.find("+")
                    reg_op = operand[:index].rstrip(" ")
                    offset_op = int(operand[index + 2:].lstrip(" "))
                    register_byte += self.register_names[reg_op[1:]]

                    # Check if the size of the number is valid
                    if not (-1 * 2**15 < offset_op < 2**15):
                        raise AssemblerError(f"Immediate constant provided too big: {self.line}")

                    encoded_number = self.__encode_number(offset_op, 16)
                    immediate_bytes += encoded_number

                elif op_type in ["memreg", "simdreg"]:
                    if self.isa == "cisc":
                        register_byte += self.register_names[operand[2:-1]]
                    else:
                        binary_line += self.register_names[operand[2:-1]]

                elif op_type == "memregoff":
                    index = operand.find("+")
                    reg_op = operand[1:index].rstrip(" ")
                    offset_op = int(operand[index + 2:-1].lstrip(" "))
                    register_byte += self.register_names[reg_op[1:]]

                    # Check if the size of the number is valid
                    if not (-1 * 2 ** 15 < offset_op < 2 ** 15):
                        raise AssemblerError(f"Immediate constant provided too big: {self.line}")

                    encoded_number = self.__encode_number(offset_op, 16)
                    immediate_bytes += encoded_number

                elif op_type.startswith("imm"):

                    # Read the number from the assembly code
                    num = int(operand[1:])

                    # RISC-Stack has to divide the number into two 6-bit bytes
                    # RISC-Accumulator and CISC have to divide the number into two 8-bit bytes
                    # Immediate constant length is undefined for Risc-Register architecture,
                    # and thus is set for every instruction
                    bit_lengths = {"risc1": "12", "risc2": "16", "risc3": op_type[3:], "cisc": "16"}
                    bit_len = int(bit_lengths[self.isa])

                    # Check if the size of the number is valid
                    if not (-1 * 2 ** (bit_len - 1) < num < 2 ** (bit_len - 1)):
                        raise AssemblerError(f"Immediate constant provided too big: {self.line}")

                    encoded_number = self.__encode_number(num, bit_len)

                    if self.isa == "cisc":
                        immediate_bytes += encoded_number
                    else:
                        binary_line += encoded_number

            else:
                raise AssemblerError(f"Provide valid operands for this instruction: {self.line}")

        if self.isa == "cisc":
            if register_byte:
                register_byte = register_byte.ljust(8, '0')
            binary_line += register_byte + immediate_bytes

        return binary_line.ljust(instruction_length, '0')

    def __valid_type(self, assembly_op, op_type):
        """
        Checks if the operand provided in assembly code is of valid type for this instruction
        :param assembly_op: str - assembly operand
        :param op_type: str - keyword with operand type
        :return: bool - whether the operand is validly encoded
        """
        # If the operand signifies a register, it should start
        # with a '%' sign and the name should exist in this architecture
        if op_type == "reg":
            return assembly_op.startswith("%") and assembly_op[1:] in self.register_names

        elif op_type == "regoff":
            index = assembly_op.find("+")
            if index == -1: return False
            reg_op = assembly_op[:index].rstrip(" ")
            offset_op = assembly_op[index + 1:].lstrip(" ")
            return self.__valid_type(reg_op, "reg") and self.__valid_type(offset_op, "imm")

        # If the operand is a memory location addressed by a register, it should look like [%reg]
        elif op_type in ["memreg", "simdreg"]:
            return (assembly_op.startswith("[") and assembly_op.endswith("]")
                    and self.__valid_type(assembly_op[1:-1], "reg"))

        # If the operand provided is a memory location with an immediate constant offset - [%reg\s+\+\s+$off]
        elif op_type == "memregoff":
            index = assembly_op.find("+")
            if index == -1: return False
            memreg_op = assembly_op[1:index].rstrip(" ")
            offset_op = assembly_op[index+1:-1].lstrip(" ")
            return (assembly_op.startswith("[") and assembly_op.endswith("]")
                    and self.__valid_type(memreg_op, "reg") and self.__valid_type(offset_op, "imm"))

        # If the operand is an immediate constant, it should start with a '$' sign and contain numbers only
        elif op_type.startswith("imm"):
            return assembly_op.startswith("$") and self.__is_number(assembly_op[1:])

    @staticmethod
    def __encode_number(number, length):
        """
        Encodes the number in the next two bytes of different sizes for RISC-Register and RISC-Stack architectures
        :param number: int, the actual number to encode
        :param length: int, the length of two bytes of encoding for the architecture
        :return: str - two lines with encoded numbers of specified length
        """
        return bin(twos_complement(number, length))[2:].rjust(length, '0')

    @staticmethod
    def __is_number(n):
        """
        Checks if the number string provided is valid
        :param n: str
        :return: bool
        """
        try:
            int(n)
            return True
        except ValueError:
            return False


class AssemblerError(Exception):
    """ Error raised by the assembler module """


if __name__ == '__main__':
    assembler = AssemblerCLI()
