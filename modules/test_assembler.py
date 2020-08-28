#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Assembly Simulator project 2020
# GNU General Public License v3.0
import unittest
import os
from modules.assembler import Assembler


# This module tests the Assembler's basic functionality
# TODO: Test everything, including CISC architecture's offsets


class TestAssembler(unittest.TestCase):
    def setUp(self):
        """ Loads the common programs for testing """
        test_programs = [('risc3', os.path.join("modules", "program_examples", "complete_risc3.asm")),
                         ('risc1', os.path.join("modules", "program_examples", "complete_risc1.asm")),
                         ('risc2', os.path.join("modules", "program_examples", "complete_risc2.asm")),
                         ('cisc', os.path.join("modules", "program_examples", "complete_cisc.asm")),
                         ('risc1', os.path.join("modules", "program_examples", "label_test_risc1.asm")),
                         ('risc2', os.path.join("modules", "program_examples", "label_test_risc2.asm")),
                         ('risc3', os.path.join("modules", "program_examples", "label_test_risc3.asm")),
                         ('cisc', os.path.join("modules", "program_examples", "label_test_cisc.asm")),
                         ('cisc', os.path.join("modules", "program_examples", "directive_test_cisc.asm"))]

        # These files were created after programs were already tested in the simulator,
        # and present correct results of the Assembler work
        # Should be used, when there are new changes in Assembler class, which might ruin some previous functionality,
        # or if we decide to try to implement Assembler class in another language, other than Python
        checked_programs = [os.path.join("modules", "program_examples", "checked_complete_risc3.bin"),
                            os.path.join("modules", "program_examples", "checked_complete_risc1.bin"),
                            os.path.join("modules", "program_examples", "checked_complete_risc2.bin"),
                            os.path.join("modules", "program_examples", "checked_complete_cisc.bin"),
                            os.path.join("modules", "program_examples", "checked_label_risc1.bin"),
                            os.path.join("modules", "program_examples", "checked_label_risc2.bin"),
                            os.path.join("modules", "program_examples", "checked_label_risc3.bin"),
                            os.path.join("modules", "program_examples", "checked_label_cisc.bin"),
                            os.path.join("modules", "program_examples", "checked_directives_cisc.bin")]

        result_list = self.assemble_programs(test_programs)

        self.complete_risc3 = result_list[0]
        with open(checked_programs[0], "r") as file:
            self.checked_complete_risc3 = file.read()

        self.complete_risc1 = result_list[1]
        with open(checked_programs[1], "r") as file:
            self.checked_complete_risc1 = file.read()

        self.complete_risc2 = result_list[2]
        with open(checked_programs[2], "r") as file:
            self.checked_complete_risc2 = file.read()

        self.complete_cisc = result_list[3]
        with open(checked_programs[3], "r") as file:
            self.checked_complete_cisc = file.read()

        self.label_risc1 = result_list[4]
        with open(checked_programs[4], "r") as file:
            self.checked_label_risc1 = file.read()

        self.label_risc2 = result_list[5]
        with open(checked_programs[5], "r") as file:
            self.checked_label_risc2 = file.read()

        self.label_risc3 = result_list[6]
        with open(checked_programs[6], "r") as file:
            self.checked_label_risc3 = file.read()

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

    def test_risc1(self):
        """ Compare resulting assembled program with a checked one for RISC1 ISA """
        self.assertEqual(self.complete_risc1, self.checked_complete_risc1)
        self.assertEqual(self.label_risc1, self.checked_label_risc1)

    def test_risc2(self):
        """ Compare resulting assembled program with a checked one for RISC2 ISA """
        self.assertEqual(self.complete_risc2, self.checked_complete_risc2)
        self.assertEqual(self.label_risc2, self.checked_label_risc2)

    def test_risc3(self):
        """ Compare resulting assembled program with a checked one for RISC3 ISA """
        self.assertEqual(self.complete_risc3, self.checked_complete_risc3)
        self.assertEqual(self.label_risc3, self.checked_label_risc3)

    def test_cisc(self):
        """ Compare resulting assembled program with a checked one for CISC ISA """
        self.assertEqual(self.complete_cisc, self.checked_complete_cisc)
        self.assertEqual(self.label_cisc, self.checked_label_cisc)
        self.assertEqual(self.directives_cisc, self.checked_directives_cisc)


if __name__ == '__main__':
    unittest.main()
