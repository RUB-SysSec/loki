"""Contains tests of pattern matcher that are a bit long to execute.
"""
# pylint: disable=relative-import

import unittest

from templates import PatternMatcherTest


class TestPatternMatcherLong(PatternMatcherTest):
    """
    More thorough tests on pattern matcher.
    """

    def test_long_reduced(self):
        'Basic negative tests'
        pattern_string = "(A ^ ~B) - B"
        test_neg = ["(x ^ y) - y", "y - (x ^ ~y)", "(x ^ ~y) - z"]
        for input_string in test_neg:
            self.generic_test_negative(input_string, pattern_string)

    def test_long_mbaxor_one(self):
        'Test positive / negative matchings for one XOR mba'
        pattern_string = "(A ^ ~B) + 2*(A | B)"

        tests_pos = ["(y | x)*2 + (x ^ ~y)", "(y | x)*2 + (~y ^ x)",
                     "(x | y)*2 + (~x ^ y)", "(y | x)*2 + (y ^ ~x)",
                     "((a + 32) ^ ~(var*5)) + ((a + 32) | (var*5))*2",
                     "((g + 45) | (12 & n))*2 + ((-g - 46) ^ (12 & n))",
                     "(g | (12 & n))*2 + ((g ^ (-1)) ^ (12 & n))"]
        for input_string in tests_pos:
            self.generic_test_positive(input_string, pattern_string)

        tests_neg = ["(x ^ y) + 2*(x | y)", "(~x ^ ~y) + 2*(x | y)",
                     "(x ^ 42) + 2*(x | 34)", "3*(x | y) + (x ^ ~y)",
                     "((g + 45) | (12 & n))*2 + ((-g - 47) ^ (12 & n))"]
        for input_string in tests_neg:
            self.generic_test_negative(input_string, pattern_string)

    def test_long_mbaxor_two(self):
        'Test negative matchings for another XOR mba'
        pattern_string = "(A ^ B) + 2*(A & B)"
        tests_neg = ["(x ^ x) + 2*(x & y)", "(x ^ ~y) + 2*(x & y)",
                     "(x ^ y) + 3*(x & y)"]
        for input_string in tests_neg:
            self.generic_test_negative(input_string, pattern_string)


if __name__ == '__main__':
    unittest.main()
