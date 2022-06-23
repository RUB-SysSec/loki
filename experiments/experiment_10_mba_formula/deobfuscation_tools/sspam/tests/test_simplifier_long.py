"""Longer tests for simplifier module
"""
# pylint: disable=relative-import

import unittest
import os

from sspam import simplifier
from templates import SimplifierTest


class TestSimplifierLong(SimplifierTest):
    """
    Longer tests for simplifier module.
    """

    def test_long_basics(self):
        'Long basic test'
        input_str = """a = 3 + x + 0
b = 4 + x - x + x
c = - 7 + a + b"""
        ref_str = """a = (3 + x)
b = (4 + x)
c = (2 * x)"""
        self.generic_test(input_str, ref_str)

    def test_samples(self):
        'Test all samples'
        samples_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   "samples")
        for samplefilename in os.listdir(samples_dir):
            fname = os.path.join(samples_dir, samplefilename)
            samplefile = open(fname, 'r')
            refstring = samplefile.readline()[2:-1]
            output_string = simplifier.simplify(fname).split('\n')[-1]
            self.assertTrue(refstring == output_string,
                            "Processing file %s: %s is not equal to %s"
                            % (samplefilename, refstring, output_string))


if __name__ == '__main__':
    unittest.main()
