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
# and the correct behaviour of all assembly isntructions

# TODO: Rework these tests with the updated memory structure (Stack, Instruction Pointer behaviour)
# TODO: Add more tests for each architecture


class TestCPU(unittest.TestCase):
    def setUp(self):
        """ Loads the common programs for testing """
        with open(os.path.join("modules", "program_examples", "assembly_test6.bin"), "r") as file:
            self.program_text = file.read()

    def test_program_loading(self):
        """ Tests the correct program loading in the memory """
        cpu_neumann = CPU("risc3", "neumann", "special", self.program_text)
        cpu_harvard = CPU("risc3", "harvard", "special", self.program_text)

        # Testing Neumann architecture
        self.assertEqual(ba2hex(cpu_neumann.program_memory.slots[1024:1024 + 16*8]), "184119011a5b5500680488080c0263fc")
        self.assertEqual(ba2hex(cpu_neumann.data_memory.slots[1024:1024 + 16*8]), "184119011a5b5500680488080c0263fc")

        # Testing Harvard architecture
        self.assertEqual(ba2hex(cpu_harvard.data_memory.slots), "0"*2048)
        self.assertEqual(ba2hex(cpu_harvard.program_memory.slots[1024:1024 + 16*8]), "184119011a5b5500680488080c0263fc")

    def test_program_loading_offset(self):
        """ Tests the correct byte program_start for each architecture """
        cpu_risc1 = CPU("risc1", "neumann", "special", self.program_text, program_start=512)
        self.assertEqual(ba2hex(cpu_risc1.program_memory.slots[512:512 + 16 * 8]), "184119011a5b5500680488080c0263fc")

        cpu_risc2 = CPU("risc2", "neumann", "special", self.program_text, program_start=512)
        self.assertEqual(ba2hex(cpu_risc2.program_memory.slots[512:512 + 16 * 8]), "184119011a5b5500680488080c0263fc")

        cpu_risc3 = CPU("risc3", "neumann", "special", self.program_text, program_start=512)
        self.assertEqual(ba2hex(cpu_risc3.program_memory.slots[512:512 + 16 * 8]), "184119011a5b5500680488080c0263fc")


if __name__ == '__main__':
    unittest.main()
