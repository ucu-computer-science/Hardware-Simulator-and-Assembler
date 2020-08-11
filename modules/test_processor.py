#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0
import os
import unittest
from bitarray.util import ba2hex

from modules.processor import CPU
from modules.assembler import Assembler

# This module tests the basic functionality of the processor module, including
# its initialization (registers, program text, memory etc.)
# and the correct behaviour of all assembly instructions

# TODO: Add more tests for each architecture


class TestCPU(unittest.TestCase):
    def setUp(self):
        """ Loads the common programs for testing """
        test_programs = [('risc1', os.path.join("modules", "demos", "risc1", 'alphabet_printout.asm')),
                         ('risc1', os.path.join("modules", "demos", "risc1", "helloworld.asm")),
                         ('risc3', os.path.join("modules", "demos", "risc3", "helloworld.asm")),
                         ('risc3', os.path.join("modules", "demos", "risc3", "alphabet_printout.asm")),
                         ('risc3', os.path.join("modules", "program_examples", "assembly_test6.asm")),
                         ('risc3', os.path.join("modules", "program_examples", "complete_risc3.asm")),
                         ('risc1', os.path.join("modules", "program_examples", "complete_risc1.asm"))]

        output_files = self.reassemble(test_programs)

        with open(output_files[0], "r") as file:
            self.risc1_program_text = file.read()
            self.risc1_alphabet = self.risc1_program_text

        with open(output_files[1], "r") as file:
            self.risc1_hello_world = file.read()

        with open(output_files[2], "r") as file:
            self.risc3_hello_world = file.read()

        with open(output_files[3], "r") as file:
            self.risc3_alphabet = file.read()

        with open(output_files[4], "r") as file:
            self.risc3_program_text = file.read()

        with open(output_files[5], "r") as file:
            self.complete_risc3 = file.read()

        with open(output_files[6], "r") as file:
            self.complete_risc1 = file.read()

    def reassemble(self, programs):
        """ Reassembles all the test programs """
        output_files = []
        for program in programs:
            with open(program[1], 'r') as file:
                program_text = file.read()
            binary_program = Assembler(program[0], program_text).binary_code
            output_path = os.path.join(os.path.dirname(program[1]),
                                       os.path.splitext(os.path.basename(program[1]))[0] + ".bin")
            output_files.append(output_path)
            with open(output_path, "w") as file:
                file.write(binary_program)
        return output_files

    def test_program_loading(self):
        """ Tests the correct program loading in the memory """
        cpu_neumann = CPU("risc3", "neumann", "special", self.risc3_program_text)
        cpu_harvard = CPU("risc3", "harvard", "special", self.risc3_program_text)

        # Testing Neumann architecture
        self.assertEqual(ba2hex(cpu_neumann.program_memory.slots[512*8:512*8 + 16*8]), "184119011a5b5500680488080c0263fc")
        self.assertEqual(ba2hex(cpu_neumann.data_memory.slots[512*8:512*8 + 16*8]), "184119011a5b5500680488080c0263fc")

        # Testing Harvard architecture
        self.assertEqual(ba2hex(cpu_harvard.data_memory.slots), "0"*2048)
        self.assertEqual(ba2hex(cpu_harvard.program_memory.slots[512*8:512*8 + 16*8]), "184119011a5b5500680488080c0263fc")

    def test_program_loading_offset(self):
        """ Tests the correct byte program_start for each architecture """
        cpu_risc1 = CPU("risc1", "neumann", "special", self.risc1_program_text, program_start=512)
        self.assertEqual(ba2hex(cpu_risc1.program_memory.slots[512*6:512*6 + 22*6]),
                         "8810479816eb0061ec00188004ea7fe40")

        # cpu_risc2 = CPU("risc2", "neumann", "special", self.riscprogram_text, program_start=512)
        # self.assertEqual(ba2hex(cpu_risc2.program_memory.slots[512*8:512*8 + 16*8]), "184119011a5b5500680488080c0263fc")

        cpu_risc3 = CPU("risc3", "neumann", "special", self.risc3_program_text, program_start=512)
        self.assertEqual(ba2hex(cpu_risc3.program_memory.slots[512*8:512*8 + 16*8]), "184119011a5b5500680488080c0263fc")

    def test_alphabet(self):
        """ Tests the correct alphabet printout for RISC1 and RISC3 architecture """
        cpu_risc1 = CPU("risc1", "harvard", "special", self.risc1_alphabet)
        cpu_risc3 = CPU("risc3", "neumann", "special", self.risc3_alphabet)

        # Skipping the needed amount of instructions
        for _ in range(50):
            cpu_risc1.web_next_instruction()
        for _ in range(35):
            cpu_risc3.web_next_instruction()

        alphabet_check = ["              ABCDEF", "GHIJKLMNOPQRSTUVWXYZ"]

        self.assertEqual(str(cpu_risc1.ports_dictionary["1"]), alphabet_check[0])
        self.assertEqual(str(cpu_risc3.ports_dictionary["1"]), alphabet_check[0])

        # Skipping the needed amount of instructions
        for _ in range(165):
            cpu_risc1.web_next_instruction()
        for _ in range(100):
            cpu_risc3.web_next_instruction()

        self.assertEqual(str(cpu_risc1.ports_dictionary["1"]), alphabet_check[1])
        self.assertEqual(str(cpu_risc3.ports_dictionary["1"]), alphabet_check[1])

    def test_risc3_hello_world(self):
        """ Tests the correct 'Hello world' workflow for RISC1 and RISC3 architecture """
        cpu_risc1 = CPU("risc1", "harvard", "special", self.risc1_hello_world)
        cpu_risc3 = CPU("risc3", "neumann", "special", self.risc3_hello_world)

        # Skipping the needed amount of instructions
        for _ in range(73):
            cpu_risc1.web_next_instruction()
        for _ in range(95):
            cpu_risc3.web_next_instruction()

        self.assertEqual(ba2hex(cpu_risc3.program_memory.slots[-192:]),
                         "00480065006c006c006f00200077006f0072006c00640021")

        self.assertEqual(str(cpu_risc1.ports_dictionary["1"]), "        Hello world!")

        self.assertEqual(str(cpu_risc3.ports_dictionary["1"]), "        Hello world!")

    def test_risc1_complete(self):
        """ Tests all of the instructions of RISC1 ISA """
        cpu = CPU("risc1", "neumann", "special", self.complete_risc1)
        cpu.web_next_instruction()

        # Checking the mov $1022 instruction
        cpu.web_next_instruction()
        tos_val = int(cpu.registers['TOS']._state.to01(), 2)
        self.assertEqual(cpu.data_memory.read_data(tos_val*8 - 16, tos_val*8).to01(), '0000001111111110')

        # Checking the mov $5 instruction
        cpu.web_next_instruction()
        tos_val = int(cpu.registers['TOS']._state.to01(), 2)
        self.assertEqual(cpu.data_memory.read_data(tos_val * 8 - 16, tos_val * 8).to01(), '0000000000000101')

        # Checking the push instruction
        cpu.web_next_instruction()
        self.assertEqual(cpu.data_memory.read_data(1024 * 8 - 16, 1024 * 8).to01(), '0000000000000101')

        # Checking the load instruction
        cpu.web_next_instruction()
        tos_val = int(cpu.registers['TOS']._state.to01(), 2)
        self.assertEqual(cpu.data_memory.read_data(tos_val * 8 - 16, tos_val * 8).to01(), '0000000000000101')

        # Checking the loadf instruction
        cpu.web_next_instruction()
        tos_val = int(cpu.registers['TOS']._state.to01(), 2)
        self.assertEqual(cpu.data_memory.read_data(tos_val * 8 - 16, tos_val * 8).to01(), '0000000000000000')

        # Checking the load $1022 instruction
        cpu.web_next_instruction()
        tos_val = int(cpu.registers['TOS']._state.to01(), 2)
        self.assertEqual(cpu.data_memory.read_data(tos_val * 8 - 16, tos_val * 8).to01(), '0000000000000101')

        # Checking the mov $0 instruction
        cpu.web_next_instruction()

        # Checking the store $128 instruction
        cpu.web_next_instruction()
        self.assertEqual(cpu.data_memory.read_data(0, 16).to01(), '0000000010000000')

        # Skipping the mov $128 instruction
        cpu.web_next_instruction()

        # Checking the storef instruction
        cpu.web_next_instruction()
        self.assertEqual(cpu.registers['FR']._state.to01(), '0000000010000000')

        # Checking the pushf instruction
        cpu.web_next_instruction()
        stack_frame = int(cpu.registers['SP']._state.to01(), 2)
        self.assertEqual(cpu.registers['FR']._state.to01(),
                         cpu.data_memory.read_data(stack_frame*8, stack_frame*8+16).to01())

        # Skipping through mov $12, mov $15 instructions
        cpu.web_next_instruction()
        cpu.web_next_instruction()

        # Checking the swap instruction
        tos_val = int(cpu.registers['TOS']._state.to01(), 2)
        self.assertEqual(cpu.data_memory.read_data(tos_val*8 - 32, tos_val*8 - 16).to01(), '0000000000001100')
        self.assertEqual(cpu.data_memory.read_data(tos_val*8 - 16, tos_val * 8).to01(), '0000000000001111')
        cpu.web_next_instruction()
        self.assertEqual(cpu.data_memory.read_data(tos_val*8 - 32, tos_val*8 - 16).to01(), '0000000000001111')
        self.assertEqual(cpu.data_memory.read_data(tos_val*8 - 16, tos_val*8).to01(), '0000000000001100')

        # Checking the dup2 instruction
        cpu.web_next_instruction()
        tos_val = int(cpu.registers['TOS']._state.to01(), 2)
        self.assertEqual(cpu.data_memory.read_data(tos_val*8 - 48, tos_val*8 - 32).to01(),
                         cpu.data_memory.read_data(tos_val*8 - 16, tos_val*8).to01())

        # Checking the dup instruction
        cpu.web_next_instruction()
        tos_val = int(cpu.registers['TOS']._state.to01(), 2)
        self.assertEqual(cpu.data_memory.read_data(tos_val * 8 - 32, tos_val * 8 - 16).to01(),
                         cpu.data_memory.read_data(tos_val * 8 - 16, tos_val * 8).to01())

        # Checking the push instruction
        cpu.web_next_instruction()
        stack_frame = int(cpu.registers['SP']._state.to01(), 2)
        tos_val = int(cpu.registers['TOS']._state.to01(), 2)
        self.assertEqual(cpu.data_memory.read_data(stack_frame * 8, stack_frame * 8 + 16).to01(),
                         cpu.data_memory.read_data(tos_val * 8, tos_val * 8 + 16).to01())

        # Skipping through mov $1 instruction
        cpu.web_next_instruction()

        # Checking the pop instruction
        cpu.web_next_instruction()
        stack_frame = int(cpu.registers['SP']._state.to01(), 2)
        tos_val = int(cpu.registers['TOS']._state.to01(), 2)
        self.assertEqual(cpu.data_memory.read_data(stack_frame * 8 - 16, stack_frame * 8).to01(),
                         cpu.data_memory.read_data(tos_val * 8 - 16, tos_val * 8).to01())

        # Skipping through the push instruction
        cpu.web_next_instruction()

        # Checking the popf instruction
        cpu.web_next_instruction()
        stack_frame = int(cpu.registers['SP']._state.to01(), 2)
        self.assertEqual(cpu.registers['FR']._state.to01(),
                         cpu.data_memory.read_data(stack_frame * 8 - 16, stack_frame*8).to01())

        # Skipping through mov $1 and mov $2 instructions
        cpu.web_next_instruction()
        cpu.web_next_instruction()

        # Checking the add instruction
        cpu.web_next_instruction()
        tos_val = int(cpu.registers['TOS']._state.to01(), 2)
        self.assertEqual(cpu.data_memory.read_data(tos_val*8 - 16, tos_val*8).to01(), '0000000000000011')

        # Skipping through mov $3, mov $2 instructions
        cpu.web_next_instruction()
        cpu.web_next_instruction()

        # Checking the sub instruction
        cpu.web_next_instruction()
        tos_val = int(cpu.registers['TOS']._state.to01(), 2)
        self.assertEqual(ba2hex(cpu.data_memory.read_data(tos_val*8-16, tos_val*8)), 'ffff')

        # Skipping through two mov instructions
        cpu.web_next_instruction()
        cpu.web_next_instruction()

        # Checking the mul instruction
        cpu.web_next_instruction()
        tos_val = int(cpu.registers['TOS']._state.to01(), 2)
        self.assertEqual(ba2hex(cpu.data_memory.read_data(tos_val*8-16, tos_val*8)), 'fffd')

        # Skipping through two mov instructions
        cpu.web_next_instruction()
        cpu.web_next_instruction()

        # Checking the div instruction
        cpu.web_next_instruction()
        tos_val = int(cpu.registers['TOS']._state.to01(), 2)
        self.assertEqual(ba2hex(cpu.data_memory.read_data(tos_val * 8 - 16, tos_val * 8)), '0003')

        # Skipping through two mov instructions
        cpu.web_next_instruction()
        cpu.web_next_instruction()

        # Checking the and instruction
        cpu.web_next_instruction()
        tos_val = int(cpu.registers['TOS']._state.to01(), 2)
        self.assertEqual(ba2hex(cpu.data_memory.read_data(tos_val*8 - 16, tos_val*8)), '0002')

        # Skipping through two mov instructions
        cpu.web_next_instruction()
        cpu.web_next_instruction()

        # Checking the or instruction
        cpu.web_next_instruction()
        tos_val = int(cpu.registers['TOS']._state.to01(), 2)
        self.assertEqual(ba2hex(cpu.data_memory.read_data(tos_val * 8 - 16, tos_val * 8)), '0007')

        # Skipping through two mov instructions
        cpu.web_next_instruction()
        cpu.web_next_instruction()

        # Checking the xor instruction
        cpu.web_next_instruction()
        tos_val = int(cpu.registers['TOS']._state.to01(), 2)
        self.assertEqual(ba2hex(cpu.data_memory.read_data(tos_val * 8 - 16, tos_val * 8)), '0005')

        # Skipping through mov $15 instruction
        cpu.web_next_instruction()

        # Checking the not instruction
        cpu.web_next_instruction()
        tos_val = int(cpu.registers['TOS']._state.to01(), 2)
        self.assertEqual(ba2hex(cpu.data_memory.read_data(tos_val * 8 - 16, tos_val * 8)), 'fff0')

        # Skipping through mov $2 instruction
        cpu.web_next_instruction()

        # Checking the lsh instruction
        cpu.web_next_instruction()
        tos_val = int(cpu.registers['TOS']._state.to01(), 2)
        self.assertEqual(ba2hex(cpu.data_memory.read_data(tos_val * 8 - 16, tos_val * 8)), '0004')

        # Checking the rsh instruction
        cpu.web_next_instruction()
        tos_val = int(cpu.registers['TOS']._state.to01(), 2)
        self.assertEqual(ba2hex(cpu.data_memory.read_data(tos_val * 8 - 16, tos_val * 8)), '0002')

        # Checking the call $2 instruction
        self.assertEqual(ba2hex(cpu.registers['IP']._state), '0265')
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['IP']._state), '0269')

        # Checking the call instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['IP']._state), '026d')

        # Checking the ret instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['IP']._state), '026a')

    def test_risc3_complete(self):
        """ Tests all of the instructions of RISC3 ISA """
        cpu = CPU("risc3", "neumann", "special", self.complete_risc3)
        cpu.web_next_instruction()

        # Check the mov_high %R00, $2 instruction
        cpu.web_next_instruction()
        self.assertEqual(cpu.registers['R00']._state.to01(), '0000001000000000')

        # Check the mov_low %R00, $-1 instruction
        cpu.web_next_instruction()
        self.assertEqual(cpu.registers['R00']._state.to01(), '0000000011111111')

        # Checking the mov_high %R00, $2 instruction
        cpu.web_next_instruction()
        self.assertEqual(cpu.registers['R00']._state.to01(), '0000001011111111')

        # Checking the mov %R01, %R00 instruction
        cpu.web_next_instruction()
        self.assertEqual(cpu.registers['R00']._state.to01(), cpu.registers['R01']._state.to01())

        # Checking the mov_low %R01, $0 instruction
        cpu.web_next_instruction()
        self.assertEqual(cpu.registers['R01']._state.to01(), '0'*16)

        # Checking the mov_high %R01, $2 instruction
        cpu.web_next_instruction()
        self.assertEqual(cpu.registers['R01']._state.to01(), '0000001000000000')

        # Checking the load %R00, [%R01] instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['R00']._state), '2002')

        # Checking the mov_low %R01, $0 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['R01']._state), '0000')

        # Checking the store [%R01], %R00 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.data_memory.slots[0:16]), ba2hex(cpu.registers['R00']._state))

        # Checking the push %R00 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.data_memory.slots[-16:]), ba2hex(cpu.registers['R00']._state))

        # Checking the pop %R01 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.data_memory.slots[-16:]), ba2hex(cpu.registers['R01']._state))

        # Checking the add %R00, %R00, %R01 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['R00']._state), '4004')

        # Checking the sub %R00, %R00, %R01 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['R00']._state), '2002')

        # Checking the mov_low %R02, $2 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['R02']._state), '0002')

        # Checking the mul %R01, %R01, %R02 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['R01']._state), '4004')

        # Checking the div %R01, %R01, %R02 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['R01']._state), '2002')

        # Checking the mov_low %R02, $5 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['R02']._state), '0005')

        # Checking the and %R00, %R01, %R02 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['R00']._state), '0000')

        # Checking the or %R00, %R01, %R02 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['R00']._state), '2007')

        # Checking the xor %R00, %R00, %R01 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['R00']._state), '0005')

        # Checking the not %R00, %R00 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['R00']._state), 'fffa')

        # Checking the mov_low %R00, $5 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['R00']._state), '0005')

        # Checking the mov_low %R02, $1 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['R02']._state), '0001')

        # Checking the rsh %R00, %R00, %R02 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['R00']._state), '0002')

        # Checking the lsh %R00, %R00, %R02 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['R00']._state), '0004')

        # Checking the call $5 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['IP']._state), '023c')

        # Checking the call $-3 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['IP']._state), '0236')

        # Checking the call %R00 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['IP']._state), '023e')

        # Checking the ret instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['IP']._state), '0238')

        # Checking the nop instruction
        self.assertEqual(cpu.instruction.to01(), '1000110000000000')
        cpu.web_next_instruction()

        # Checking the jmp $3 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['IP']._state), '0240')

        # Checking the jmp %R00 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['IP']._state), '0248')

        # Checking the mov_low %R00, $2 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['R00']._state), '0002')

        # Checking the cmp %R00, %R02 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['FR']._state), '0000')

        # Checking the je $-2 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['IP']._state), '024e')

        # Checking the jne $-6 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['IP']._state), '0242')

        # Checking the cmp %R00, $2 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['FR']._state), '0004')

        # Checking the je $6 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['IP']._state), '0250')

        # Checking the cmp %R00, $6 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['FR']._state), '0001')

        # Checking the jg $5 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['IP']._state), '0254')

        # Checking the nop instruction
        self.assertEqual(cpu.instruction.to01(), '1000110000000000')
        cpu.web_next_instruction()

        # Checking the jge $5 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['IP']._state), '0258')

        # Checking the jl $2 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['IP']._state), '025c')

        # Checking the jle $2 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['IP']._state), '0260')

        # Checking the cmp %R00, $2 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['FR']._state), '0004')

        # Checking the jle $2 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['IP']._state), '0266')

        # Checking the jl $2 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['IP']._state), '0268')

        # Checking the mov_low %R00, $64 instruction
        cpu.web_next_instruction()
        self.assertEqual(ba2hex(cpu.registers['R00']._state), '0040')

        # Checking the out $1, %R00 instruction
        cpu.web_next_instruction()
        self.assertEqual(str(cpu.ports_dictionary['1']), '                   @')

        # Checking the in %R00, $1 instruction
        cpu.web_next_instruction()
        cpu.input_finish(bin(ord("a"))[2:])
        self.assertEqual(ba2hex(cpu.registers['R00']._state), '0061')


if __name__ == '__main__':
    unittest.main()
