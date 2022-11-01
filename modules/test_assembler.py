#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0
import unittest
import os
from modules.assembler import Assembler, AssemblerError


# This module tests the Assembler's basic functionality
# TODO: Test everything, including CISC architecture's offsets

        
class TestAssembler(unittest.TestCase):
    def setUp(self):
        """ Loads the common programs for testing """
        test_programs = [('risc', os.path.join("modules", "program_examples", "complete_risc.asm")),
                         ('stack', os.path.join("modules", "program_examples", "complete_stack.asm")),
                         ('accumulator', os.path.join("modules", "program_examples", "complete_accumulator.asm")),
                         ('cisc', os.path.join("modules", "program_examples", "complete_cisc.asm")),
                         ('stack', os.path.join("modules", "program_examples", "label_test_stack.asm")),
                         ('accumulator', os.path.join("modules", "program_examples", "label_test_accumulator.asm")),
                         ('risc', os.path.join("modules", "program_examples", "label_test_risc.asm")),
                         ('cisc', os.path.join("modules", "program_examples", "label_test_cisc.asm")),
                         ('cisc', os.path.join("modules", "program_examples", "directive_test_cisc.asm"))]

        # These files were created after programs were already tested in the simulator,
        # and present correct results of the Assembler work
        # Should be used, when there are new changes in Assembler class, which might ruin some previous functionality,
        # or if we decide to try to implement Assembler class in another language, other than Python
        checked_programs = [os.path.join("modules", "program_examples", "checked_complete_risc.bin"),
                            os.path.join("modules", "program_examples", "checked_complete_stack.bin"),
                            os.path.join("modules", "program_examples", "checked_complete_accumulator.bin"),
                            os.path.join("modules", "program_examples", "checked_complete_cisc.bin"),
                            os.path.join("modules", "program_examples", "checked_label_stack.bin"),
                            os.path.join("modules", "program_examples", "checked_label_accumulator.bin"),
                            os.path.join("modules", "program_examples", "checked_label_risc.bin"),
                            os.path.join("modules", "program_examples", "checked_label_cisc.bin"),
                            os.path.join("modules", "program_examples", "checked_directives_cisc.bin")]

        result_list = self.assemble_programs(test_programs)

        self.complete_risc = result_list[0]
        with open(checked_programs[0], "r") as file:
            self.checked_complete_risc = file.read()

        self.complete_stack = result_list[1]
        with open(checked_programs[1], "r") as file:
            self.checked_complete_stack = file.read()

        self.complete_accumulator = result_list[2]
        with open(checked_programs[2], "r") as file:
            self.checked_complete_accumulator = file.read()

        self.complete_cisc = result_list[3]
        with open(checked_programs[3], "r") as file:
            self.checked_complete_cisc = file.read()

        self.label_stack = result_list[4]
        with open(checked_programs[4], "r") as file:
            self.checked_label_stack = file.read()

        self.label_accumulator = result_list[5]
        with open(checked_programs[5], "r") as file:
            self.checked_label_accumulator = file.read()

        self.label_risc = result_list[6]
        with open(checked_programs[6], "r") as file:
            self.checked_label_risc = file.read()

        self.label_cisc = result_list[7]
        with open(checked_programs[7], "r") as file:
            self.checked_label_cisc = file.read()

        self.directives_cisc = result_list[8]
        with open(checked_programs[8], "r") as file:
            self.checked_directives_cisc = file.read()

    @staticmethod
    def assemble_programs(programs):
        """ Reassembles all the test programs """
        result_list = []
        for program in programs:
            with open(program[1], 'r') as file:
                program_text = file.read()
            binary_program = Assembler(program[0], program_text).binary_code
            result_list.append(binary_program)
        return result_list

    def test_stack(self):
        """ Compare resulting assembled program with a checked one for Stack ISA """
        self.assertEqual(self.complete_stack, self.checked_complete_stack)
        self.assertEqual(self.label_stack, self.checked_label_stack)

    def test_accumulator(self):
        """ Compare resulting assembled program with a checked one for Accumulator ISA """
        self.assertEqual(self.complete_accumulator, self.checked_complete_accumulator)
        self.assertEqual(self.label_accumulator, self.checked_label_accumulator)

    def test_risc(self):
        """ Compare resulting assembled program with a checked one for RISC ISA """
        self.assertEqual(self.complete_risc, self.checked_complete_risc)
        self.assertEqual(self.label_risc, self.checked_label_risc)

    def test_cisc(self):
        """ Compare resulting assembled program with a checked one for CISC ISA """
        self.assertEqual(self.complete_cisc, self.checked_complete_cisc)
        self.assertEqual(self.label_cisc, self.checked_label_cisc)
        self.assertEqual(self.directives_cisc, self.checked_directives_cisc)

    def test_errors(self):
        """ Test if Assembler raises correct errors (test some of them). """
        with self.assertRaises(AssemblerError):
            Assembler("stack", "mov_low %R00, $4")
        with self.assertRaises(AssemblerError):
            Assembler("risc", "mov_low $4, $0")
        with self.assertRaises(AssemblerError):
            Assembler("stack", ".anime%")
        with self.assertRaises(AssemblerError):
            Assembler("stack", ".anime 024")


if __name__ == '__main__':
    unittest.main()
