"""Test pre-processing passes.

- TestShiftMult
- TestSubToMult
- TestRemoveUselessAnd
"""
# pylint: disable=relative-import

import unittest

from sspam import pre_processing
import templates


class TestShiftMult(templates.AstCompCase):
    """
    Test pre-processing that transforms shifts in mults.
    """

    def test_basics(self):
        'Simple tests for shift -> mult replacement'
        tests = [("x << 1", "x*2"), ("(y*32) << 1", "(y*32)*2"),
                 ("var << 4", "var*16"), ("3 << var", "3 << var"),
                 ("(x ^ y) + (x << 1)", "(x ^ y) + 2*x")]
        self.generic_AstCompTest(tests, pre_processing.ShiftToMult())


class TestSubToMult(templates.AstCompCase):
    """
    Test pre-processing that transforms subs in mults of -1.
    """

    def test_basics(self):
        'Simple tests for sub -> -1 mult replacement'
        tests = [("-x", "(-1)*x"), ("x - 3", "x + (-1)*3"),
                 ("- x - y", "(-1)*x + (-1)*y")]
        self.generic_AstCompTest(tests, pre_processing.SubToMult())


class TestRemoveUselessAnd(templates.AstCompCase):
    """
    Test pre-processing removing AND 0xFF...FF
    """

    def test_basics(self):
        'Simple tests for removing useless ands'
        tests = [("x & 255", "x", 8), ("x & 255", "x & 255", 32),
                 ("x & 65535", "x", 16), ("x & 255", "x & 255", 16)]
        for instring, refstring, nbits in tests:
            remov = pre_processing.RemoveUselessAnd(nbits)
            self.generic_AstCompTest(instring, refstring, remov)


if __name__ == '__main__':
    unittest.main()
