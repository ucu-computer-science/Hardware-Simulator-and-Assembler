#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0

# This one of the most important modules of the Hardware Simulator that translates
# mnemonics into binary code

#     Is supposed to handle a few ISA architectures:
#         * Stack
#         * Accumulator
#         * RISC Register
#         * CISC Register architectures

# Basic workflow of the Assembler is as follows:
#   * Command line interface checks provided program's ISA and passes code to the actual Assembler
#   * Assembler loads instructions for the provided ISA from instructions.json and preprocesses the code
#   * Translate instructions line by line:
#       * Separate instruction itself from operands
#       * Find correct encoding of that instruction, considering special case of 5-bit opcodes
#       * Check if the operand provided is of the type needed, if yes, encode and add it to the current line
#           (more about work with instructions.json below)
#   * Return a complete binary code of the program

# Encoding operands with information from instructions.json:
#   * Check if valid operands for that instruction were provided and if they are written correctly
#   * Add "reg" or "fr" ("memreg" or "simdreg") operands names to the binary line (or register byte for CISC)
#   * Encode register (or memregs) with offset and add its encoded value to immediate_bytes
#   * Encode immediate value:
#       * Decode the label if it's mentioned, otherwise read the number from the assembly instruction
#   * For CISC left adjust register byte and add it to the binary line with immediate bytes

# Decoding directives:
#   * Search for a correct pattern in the line
#   * If an integer is provided within required limits: return its value
#   * Decode characters in the string one by one, add their ASCII codes to the result and return it

# Resulting binary code is provided to the processor and executed

# TODO: There is more though, instructions.json is pretty inconsistent between different
#  architectures as it was all done on the go, and is under-documented


import os
import re
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
        self.jump_label_allowed = ["jmp", "call", "je", "jne", "jl", "jle", "jg", "jge", "jc"]
        self.mov_label_allowed = ["mov", "load", "store", "push", "mov_low", "mov_high", "cmp", "cmpe", "cmpb", "mul",
                                  "div"]

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

        # Preprocess the text, delete the comments and empty lines, remember labels and directives
        text = self.preprocess(text)

        # Divide the program into lines
        for index, line in enumerate(text):
            line = line.rstrip(" ")
            # Check if its an empty line or a comment line, skip if yes
            if line.strip(" ").startswith("#") or line.isspace() or not line:
                continue
            self.line = line

            # Split instruction name and operands
            binary_line = ""
            arguments = line.split()
            assembly_instruction, operands = arguments[0], ''.join(arguments[1:]).split(',')
            if len(operands) == 1 and operands[0] == '':
                operands = []

            # Check if the instruction actually exists for this architecture
            if assembly_instruction not in self.instructions:
                raise AssemblerError(f"Not valid assembly instruction: {assembly_instruction}")

            # Get the list of encodings for this assembly instruction
            instructions_info = self.instructions[assembly_instruction]

            # If this assembly instruction has a few different opcodes depending on the type of operands
            # we check every possible option until we find the one we needed
            for instruction_info in instructions_info:
                try:

                    # Low and High byte moves have 5-bit opcodes, a special case
                    if assembly_instruction in ["mov_low", "mov_high"] and len(instruction_info[0]) != 5:
                        instruction_info[0] = instruction_info[0][:-1]

                    binary_line = self.__encode_operands(operands, instruction_info, assembly_instruction, index)
                    break
                except AssemblerError:
                    continue

            # If all of the opcode options were wrong, raise the error
            if not binary_line:
                raise AssemblerError(f"Provide valid operands for this instruction: {line}")

            binary_code += binary_line + "\n"

        return binary_code

    def preprocess(self, text : str):
        """
        Preprocesses the assembly code, finds any directives and collects the needed info on them

        :param text: str - the text of the assembly program
        """
        result_text = []

        # Remembering all instances and values of labels of two types
        self.jump_labels = dict()
        self.mov_labels = dict()


        text = text.split("\n")
        text_no_comments = []

        for line in text:

            line_no_comment = line.split("#", 1)[0].strip()
            if line_no_comment:

                text_no_comments.append(line_no_comment)
        
        # text = "\n".join(text_no_comments)
            

        for line in text_no_comments:
            line = line.rstrip(" ")

            # Check if its an empty line or a comment line, skip it if yes
            if line.strip(" ").startswith("."):

                line = line.strip(" ")[1:]

                words = line.split(" ")
                if not words[0].isalnum():
                    raise AssemblerError(f"Provide valid label: {line}")
                if words[0] in self.jump_labels or words[0] in self.mov_labels:
                    raise AssemblerError(f"Labels can not be reassigned or duplicated: {line}")

                # If only the label is mentioned, it specifies a jump location and points to the next instruction
                if len(words) == 1:
                    self.jump_labels[line] = len(result_text)

                # If the label is mentioned with directive specification and its value, we have to encode it into memory
                elif len(words) == 3:
                    if words[1] == "db":
                        self.mov_labels[words[0]] = self.__decode_directive(True, words[2])
                    elif words[1] == "dw":
                        self.mov_labels[words[0]] = self.__decode_directive(False, words[2])
                    else:
                        raise AssemblerError("Provide a valid assembly directive")

                # Else, it's a wrong format of the directive
                else:
                    raise AssemblerError(
                        "Provide a valid assembly directive: either just '.label' or '.label db|dw value")

            elif not (line.strip(" ").startswith("#") or line.isspace() or not line):
                result_text.append(line)

        return result_text

    @staticmethod
    def __decode_directive(is_byte, value):
        """
        Decodes operands for directives (db, dw)

        :param is_byte: bool - to encode value in a byte or word
        :param value: str - an operand to encode
        """
        # We just figure out what's being encoded into bits - a number (which should fit in 8/16 bits) or a string of
        # characters (every ASCII character is 1 byte), and return the value we found
        limits = (-2 ** 7 + 1, 2 ** 8) if is_byte else (-2 ** 15 + 1, 2 ** 16)
        int_pattern = r"^\d+$"
        str_pattern = r"^\"[a-zA-Z0-9\\]+\"$"

        # Decode an integer
        if re.search(int_pattern, value) is not None:
            value = int(value)
            if limits[0] <= value <= limits[1]:
                return value

        # Decode a string into numbers
        elif re.search(str_pattern, value) is not None:
            result = []
            index = 1
            while index < (len(value) - 1):
                char = value[index]
                # Decode a number encoded in a string of characters
                if char == "\\":
                    index += 1
                    if value[index:index+2] == "0x":
                        index += 2
                        number = int(value[index:index+3], 16)
                        index += 3
                    else:
                        number = int(value[index:index + 3])
                        index += 3
                    if 0 <= number <= 255:
                        result.append(number)
                    else:
                        raise AssemblerError("Provide a valid assembly directive operand")

                # Else, just figure out the ASCII code of the character and remember it
                else:
                    result.append(ord(char))
                    index += 1

            return result

        raise AssemblerError("Provide a valid assembly directive operand")

    def __encode_operands(self, operands, instruction_info, instruction_name, instruction_index):
        """
        Encodes the operands given an opcode and operands types
        :param operands: list - list of operands-strings
        :param instruction_info: list - of instruction encoding and operand types
        :param instruction_name: str - a name of the assembly instruction
        :param instruction_index: int - index of the current instruction
        """
        binary_line = instruction_info[0]
        types = instruction_info[1]

        # Eliminate processor-only information in type lists
        if "one" in types:
            types.remove("one")

        instruction_length = self.instruction_size[0]
        if self.isa == "cisc":
            register_byte = ""
            immediate_bytes = ""

        if len(operands) != len(types):
            raise AssemblerError(f"Provide valid operands for this instruction: {self.line}")

        # TODO: This probably could be moved to a separate function to allow for normal recursion calls

        # Check if the operand provided is of the type needed, if yes, encode and add it to the current line
        for index, operand in enumerate(operands):
            if self.__valid_type(operand, op_type := types[index], instruction_name):

                # Encode the operand properly and add it to the line
                if op_type == "reg" or op_type == "fr":
                    if self.isa == "cisc":
                        register_byte += self.register_names[operand[1:]]
                    else:
                        binary_line += self.register_names[operand[1:]]

                elif op_type == "regoff":

                    operand = operand.replace(" ", "")
                    if (index := operand.find("+")) != -1:
                        operand_sign = "+"
                    elif (index := operand.find("-")) != -1:
                        operand_sign = "-"

                    reg_op = operand[:index]
                    offset_op = int(operand[index + 2:])
                    register_byte += self.register_names[reg_op[1:]]

                    # Check if the size of the number is valid
                    if not (-1 * 2 ** 15 < offset_op < 2 ** 15):
                        raise AssemblerError(f"Immediate constant provided too big: {self.line}")

                    if operand_sign == "-":
                        offset_op = -1 * offset_op

                    encoded_number = self.__encode_number(offset_op, 16)
                    immediate_bytes += encoded_number

                elif op_type in ["memreg", "simdreg"]:
                    if self.isa == "cisc":
                        register_byte += self.register_names[operand[2:-1]]
                    else:
                        binary_line += self.register_names[operand[2:-1]]

                elif op_type == "memregoff":

                    operand = operand.replace(" ", "")
                    num_start = operand.find("$")

                    if (index := operand.find("+")) != -1:
                        operand_sign = "+"
                    elif (index := operand.find("-")) != -1:
                        operand_sign = "-"

                    reg_op = operand[1:index]
                    try:
                        offset_op = int(operand[index + 2:-1])
                    except ValueError:
                        label_check = operand[index + 2:-1]
                        if label_check in self.mov_labels:
                            value = self.mov_labels[label_check]
                            if isinstance(value, int):
                                if num_start != -1:
                                    raise AssemblerError("Provide valid assembly directives")
                                offset_op = value
                            elif isinstance(value, list):
                                if num_start == -1:
                                    offset_op = value[0]
                                else:
                                    mov_index = int(operand[num_start + 1:])
                                    if not (0 <= mov_index < len(value)):
                                        raise AssemblerError("Provide a valid assembly directive offset")
                                    num = value[mov_index]
                        else:
                            raise AssemblerError("Provide valid assembly directives")
                    register_byte += self.register_names[reg_op[1:]]

                    # Check if the size of the number is valid
                    if not (-1 * 2 ** 15 < offset_op < 2 ** 15):
                        raise AssemblerError(f"Immediate constant provided too big: {self.line}")

                    if operand_sign == "-":
                        offset_op = -1 * offset_op

                    encoded_number = self.__encode_number(offset_op, 16)
                    immediate_bytes += encoded_number

                elif op_type.startswith("imm"):
                    operand = operand.replace(" ", "")
                    num_start = operand.find("$")
                    label_check = operand[1:] if num_start == -1 else operand[1:num_start - 1]

                    # Decode the label if it's mentioned, otherwise read the number from the assembly instruction
                    # There are two possible types of labels:
                    # * one specifies the instruction to jump to, in that case we figure out the offset and encode it
                    # * the other references a location in memory, and might also include offsets, we encode bytes or words
                    if instruction_name in self.jump_label_allowed and operand.startswith(
                            ".") and label_check in self.jump_labels:
                        num = (self.jump_labels[label_check] - instruction_index)
                    elif instruction_name in self.mov_label_allowed and operand.startswith(
                            ".") and label_check in self.mov_labels:
                        value = self.mov_labels[label_check]
                        if isinstance(value, int):
                            if num_start != -1:
                                raise AssemblerError("Provide valid assembly directives")
                            num = value
                        elif isinstance(value, list):
                            if num_start == -1:
                                num = value[0]
                            else:
                                mov_index = int(operand[num_start + 1:])
                                if not (0 <= mov_index < len(value)):
                                    raise AssemblerError("Provide a valid assembly directive offset")
                                num = value[mov_index]
                    else:
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

    def __valid_type(self, assembly_op, op_type, instruction_name, recursive=False):
        """
        Checks if the operand provided in assembly code is of valid type for this instruction
        :param assembly_op: str - assembly operand
        :param op_type: str - keyword with operand type
        :param instruction_name: str - a name of the assembly instruction
        :return: bool - whether the operand is validly encoded
        """
        # If the operand signifies a register, it should start
        # with a '%' sign and the name should exist in this architecture
        if op_type == "reg":
            return ((assembly_op.startswith("%") and assembly_op[1:] in self.register_names) or
                    (instruction_name in self.mov_label_allowed and assembly_op[1:] in self.mov_labels and recursive))

        elif op_type == "regoff":
            index_plus = assembly_op.find("+")
            index_minus = assembly_op.find("-")
            index_num = assembly_op.find("$")

            if ((index_plus == -1 and index_minus == -1) or
                    (index_plus != -1 and index_minus != -1 and (max(index_plus, index_minus) < index_num))):
                return False

            if -1 < index_minus < index_num:
                index = index_minus
            elif -1 < index_plus < index_num:
                index = index_plus

            reg_op = assembly_op[:index].rstrip(" ")
            offset_op = assembly_op[index + 1:].lstrip(" ")
            return ((self.__valid_type(reg_op, "reg", instruction_name)
                     and self.__valid_type(offset_op, "imm", instruction_name)) or
                    (recursive and self.__valid_type(reg_op, "reg", instruction_name, recursive=True)
                     and self.__valid_type(offset_op, "imm", instruction_name)))

        # If the operand is a memory location addressed by a register, it should look like [%reg]
        elif op_type in ["memreg", "simdreg"]:
            return (assembly_op.startswith("[") and assembly_op.endswith("]")
                    and self.__valid_type(assembly_op[1:-1], "reg", instruction_name))

        # If the operand provided is a memory location with an immediate constant offset - [%reg\s+\+\s+$off]
        elif op_type == "memregoff":
            index_plus = assembly_op.find("+")
            index_minus = assembly_op.find("-")
            index_num = max(assembly_op.find("$"), assembly_op.find("."))

            if ((index_plus == -1 and index_minus == -1) or
                    (index_plus != -1 and index_minus != -1 and (max(index_plus, index_minus) < index_num))):
                return False

            if -1 < index_minus < index_num:
                index = index_minus
            elif -1 < index_plus < index_num:
                index = index_plus

            memreg_op = assembly_op[1:index].rstrip(" ")
            offset_op = assembly_op[index + 1:-1].lstrip(" ")
            return (assembly_op.startswith("[") and assembly_op.endswith("]")
                    and self.__valid_type(memreg_op, "reg", instruction_name) and
                    self.__valid_type(offset_op, "imm", instruction_name))

        # If the operand is an immediate constant, it should start with a '$' sign and contain numbers only
        # Valid labels are also allowed, they should appear anywhere in the program and start with a '.'
        # Labels are of two types: specifying the jump offset, or some value from the macro value in memory
        elif op_type.startswith("imm"):
            result = [assembly_op.startswith("$") and self.__is_number(assembly_op[1:])]
            if instruction_name in self.jump_label_allowed:
                result.append(assembly_op.startswith(".") and assembly_op[1:] in self.jump_labels)
            if instruction_name in self.mov_label_allowed:
                result.append(assembly_op.startswith(".") and
                              (assembly_op[1:] in self.mov_labels or self.__valid_type(assembly_op, "regoff",
                                                                                       instruction_name,
                                                                                       recursive=True)))
            return any(result)

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
