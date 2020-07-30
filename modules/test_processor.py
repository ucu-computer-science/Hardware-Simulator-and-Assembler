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

        with open(os.path.join("modules", "demos", "risc3", "helloworld.bin"), "r") as file:
            self.risc3_hello_world = file.read()

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
        self.assertEqual(ba2hex(cpu_risc1.program_memory.slots[512*6:512*6 + 28*6]),
                         "8819620648818e2062881866048ac00ec001a7ff00")

        # cpu_risc2 = CPU("risc2", "neumann", "special", self.riscprogram_text, program_start=512)
        # self.assertEqual(ba2hex(cpu_risc2.program_memory.slots[512*8:512*8 + 16*8]), "184119011a5b5500680488080c0263fc")

        cpu_risc3 = CPU("risc3", "neumann", "special", self.risc3_program_text, program_start=512)
        self.assertEqual(ba2hex(cpu_risc3.program_memory.slots[512*8:512*8 + 16*8]), "184119011a5b5500680488080c0263fc")

    def test_alphabet(self):
        """ Tests the correct alphabet printout for RISC3 architecture """
        cpu_risc3 = CPU("risc3", "neumann", "special", self.risc3_alphabet)
        for _ in range(35):
            cpu_risc3.web_next_instruction()

        self.assertEqual(cpu_risc3.ports_dictionary["1"]._state.tobytes().decode("ascii"),
                         "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00ABCDEF")

        for _ in range(100):
            cpu_risc3.web_next_instruction()

        self.assertEqual(cpu_risc3.ports_dictionary["1"]._state.tobytes().decode("ascii"),
                         "GHIJKLMNOPQRSTUVWXYZ")

        print(ba2hex(cpu_risc3.program_memory.slots))

    def test_hello_world(self):
        """ Tests the correct 'Hello world' workflow for RISC3 architecture """
        cpu_risc3 = CPU("risc3", "neumann", "special", self.risc3_hello_world)
        for _ in range(95):
            cpu_risc3.web_next_instruction()

        self.assertEqual(ba2hex(cpu_risc3.program_memory.slots[-192:]),
                         "00480065006c006c006f00200077006f0072006c00640021")

        self.assertEqual(cpu_risc3.ports_dictionary["1"]._state.tobytes().decode("ascii"),
                         "\x00\x00\x00\x00\x00\x00\x00\x00Hello world!")


if __name__ == '__main__':
    unittest.main()
