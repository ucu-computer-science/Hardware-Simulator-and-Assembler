#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0
import os
import unittest
from bitarray.util import ba2hex

from modules.processor import CPU

# This module tests the basic functionality of the processor module, including
# its initialization (registers, program text, memory etc.)
# and the correct behaviour of all assembly instructions

# TODO: Add more tests for each architecture


class TestCPU(unittest.TestCase):
    def setUp(self):
        """ Loads the common programs for testing """
        with open(os.path.join("modules", "demos", "risc1", "alphabet_printout.bin"), "r") as file:
            self.risc1_program_text = file.read()

        with open(os.path.join("modules", "demos", "risc1", "helloworld.bin"), "r") as file:
            self.risc1_hello_world = file.read()

        with open(os.path.join("modules", "demos", "risc3", "helloworld.bin"), "r") as file:
            self.risc3_hello_world = file.read()

        with open(os.path.join("modules", "demos", "risc1", "alphabet_printout.bin"), "r") as file:
            self.risc1_alphabet = file.read()

        with open(os.path.join("modules", "demos", "risc3", "alphabet_printout.bin"), "r") as file:
            self.risc3_alphabet = file.read()

        with open(os.path.join("modules", "program_examples", "assembly_test6.bin"), "r") as file:
            self.risc3_program_text = file.read()

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

        self.assertEqual(cpu_risc1.ports_dictionary["1"]._state.tobytes().decode("ascii"), alphabet_check[0])
        self.assertEqual(cpu_risc3.ports_dictionary["1"]._state.tobytes().decode("ascii"), alphabet_check[0])

        # Skipping the needed amount of instructions
        for _ in range(165):
            cpu_risc1.web_next_instruction()
        for _ in range(100):
            cpu_risc3.web_next_instruction()

        self.assertEqual(cpu_risc1.ports_dictionary["1"]._state.tobytes().decode("ascii"), alphabet_check[1])
        self.assertEqual(cpu_risc3.ports_dictionary["1"]._state.tobytes().decode("ascii"), alphabet_check[1])

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

        self.assertEqual(cpu_risc1.ports_dictionary["1"]._state.tobytes().decode("ascii"),
                         "        Hello world!")

        self.assertEqual(cpu_risc3.ports_dictionary["1"]._state.tobytes().decode("ascii"),
                         "        Hello world!")

    def test_risc3_complete(self):
        """ Tests all of the instructions of RISC3 ISA """


if __name__ == '__main__':
    unittest.main()
