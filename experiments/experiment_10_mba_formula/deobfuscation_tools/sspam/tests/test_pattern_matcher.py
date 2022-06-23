"""Tests for pattern matcher script.

This module contains tests for the pattern matcher module.

Tested features are:
  - pure pattern matcher with various situations
  - pattern replacement
"""
# pylint: disable=relative-import

import ast
import unittest

from sspam import pattern_matcher, pre_processing
from sspam.tools import asttools
from sspam.tools.flattening import Flattening
from templates import PatternMatcherTest


class TestPatternMatcher(PatternMatcherTest):
    """
    Test for false positive / negative matchings.
    """

    def test_reduced(self):
        'Small tests for basic pattern matching'
        pattern_string = "(A ^ ~B) + B"
        tests_pos = ["(x ^ ~y) + y", "(x ^ ~y) + y", "(x ^ ~35) + 35",
                     "(42 ^ ~y) + y", "((x*a) ^ var) + ~var",
                     "(42 ^ x) + 213", "45 + (x ^ 210)",
                     "(42 ^ (a*x + b)) + 213", "((g ^ 23) ^ x) + (g ^ 232)"]
        for input_string in tests_pos:
            self.generic_test_positive(input_string, pattern_string)
        pattern_string = "(A ^ ~B) - B"
        test_pos = ["(x ^ ~y) - y", "(x ^ 45) - 210"]
        for input_string in test_pos:
            self.generic_test_positive(input_string, pattern_string)

    def test_csts(self):
        'Tests containing constants'
        test_pos = [("x + 172", "A + 2*B"),
                    ("x + 8", "A + B*2"),
                    ("x - 45 + 45", "A + B - B"),
                    ("254*x + 255", "-2*A - 1")]
        for input_string, patt_string in test_pos:
            self.generic_test_positive(input_string, patt_string, True)
        test_neg = [("x + 9", "B*2 + A")]
        for input_string, patt_string in test_neg:
            self.generic_test_negative(input_string, patt_string, True)

    def test_mod(self):
        'Tests where modulo on constants is useful'
        test_pos = [("(x | 54) + 255*(x & 54)", "(A | B) - (A & B)"),
                    ("254*x + 255", "-2*A - 1")]
        for input_string, patt_string in test_pos:
            self.generic_test_positive(input_string, patt_string, True)

    def test_subs(self):
        'Tests with substractions (with pre-processing)'
        pattern_string = "-(A ^ ~B) - (A | B)"
        test_pos = ["-(43 ^ ~tmp2) - (43 | tmp2)",
                    "-(43 ^ ~tmp2) - (tmp2 | 43)",
                    "-(~tmp2 ^ 43) - (43 | tmp2)"]
        for input_string in test_pos:
            self.generic_test_positive(input_string, pattern_string, True)
        pattern_string = "A + B - 2*(A & B)"
        test_pos = ["x + 108 - 2*(x & 108)", "-2*(x & 108) + x + 108",
                    "(x & 108)*(-2) + x + 108",
                    "254*(x & y) + x + y"]
        for input_string in test_pos:
            self.generic_test_positive(input_string, pattern_string, True)

    def test_fcts(self):
        'Test with pattern containing a function'
        pattern_string = "Fun(A)"
        tests = ["Fun(x)", "Fun(2*y + 34)", "Fun(var + f(x))", "Fun(0)"]
        for input_string in tests:
            self.generic_test_positive(input_string, pattern_string, False)
        self.generic_test_negative("fun(a)", pattern_string, False)
        pattern_string = "Fun(A, g(B))"
        self.generic_test_positive("Fun(x, g(y))", pattern_string, False)
        self.generic_test_negative("Fun(x)", pattern_string, False)
        pattern_string = "Fun(A,B,C)"
        self.generic_test_positive("Fun(x,y,z)", pattern_string, False)
        self.generic_test_negative("Fun(a,b)", pattern_string, False)
        pattern_string = "A + (fun(8) & B)"
        self.generic_test_negative("(x + 1)", pattern_string, True)

    def test_mbaxor_one(self):
        'Test positive / negative matchings for one XOR mba'
        pattern_string = "(A ^ ~B) + 2*(A | B)"

        tests_pos = ["(x ^ ~y) + 2*(x | y)", "(x | y)*2 + (x ^ ~y)",
                     "(x ^ ~45) + (45 | x)*2", "(x ^ 210) + 2*(x | 45)",
                     "((g ^ 23) | (a*x + b))*2 + ((a*x + b) ^ (g ^ 232))"]
        for input_string in tests_pos:
            self.generic_test_positive(input_string, pattern_string)

        # test with pre-processing
        tests_preproc = ["(x ^ ~y) + ((x | y) << 1)"]
        for input_string in tests_preproc:
            self.generic_test_positive(input_string, pattern_string, True)

    def test_mbaxor_two(self):
        'Test positive / negative matchings for another XOR mba'
        pattern_string = "(A ^ B) + 2*(A & B)"

        test_pos = ["(x ^ y) + 2*(x & y)", "(x ^ 35) + 2*(x & 35)",
                    "(y & 78)*2 + (y ^ 78)", "(x ^ ~y) + 2*(x & ~y)",
                    "((x + 2) ^ (y*3)) + ((x + 2) & (y*3))*2"]
        for input_string in test_pos:
            self.generic_test_positive(input_string, pattern_string)

    def test_mba_three(self):
        'Test positive / negative for an anoying MBA'
        pattern_string = "A - B + (~(2*A) & 2*B)"
        test_pos = ["x + (~(2*x) & 2*y) - y", "x + (~(2*x) & 90) + 211",
                    "x + ((-(2*x) - 1) & 90) + 211",
                    "x + ((254*x + 255) & 90) + 211"]
        for input_string in test_pos:
            self.generic_test_positive(input_string, pattern_string, True)

    def test_mba_four(self):
        'Test for MBA requiring to test with right nodes before left nodes'
        pattern_string = "-(~(2*A) & 2*B) -A"
        test_pos = ["-((-2*(x ^ 214) - 1) & 172) - (x ^ 214)",
                    "-((254*(x ^ 214) + 255) & 172) - (x ^ 214)"]
        for input_string in test_pos:
            self.generic_test_positive(input_string, pattern_string, True)

    def test_two_mult(self):
        'Test for equivalence of 2*(...) and something else with z3'
        pattern_string = "2*(A & B) + A + B"
        test_pos = ["2*(x & y) + x + y"]
        for input_string in test_pos:
            self.generic_test_positive(input_string, pattern_string)

    def test_flattened(self):
        'Test positive matchings for flattened ast'
        pattern_string = "A + 2*B + 3*C"
        test_pos = ["x + 2*y + 3*z", "3*z + 2*y + x", "2*y + 3*z + x"]
        for input_string in test_pos:
            self.generic_test_positive(input_string, pattern_string, True)

        # actual pre-processing only flattens ADD nodes, but this test
        # is for code coverage
        test_neg = ast.parse("x ^ 2*y ^ 2*z")
        test_neg = pre_processing.all_preprocessings(ast.parse(test_neg))
        test_neg = Flattening().visit(test_neg)
        patt_ast = ast.parse(pattern_string)
        patt_ast = pre_processing.all_preprocessings(patt_ast)
        patt_ast = Flattening(ast.Add).visit(patt_ast)
        pat = pattern_matcher.PatternMatcher(test_neg)
        self.assertFalse(pat.visit(test_neg, patt_ast))

    def test_with_nbits(self):
        'Test with nbits given by the user'
        tests = [("(x ^ 52) + 2*(x | 203)", 8),
                 ("(x ^ 789) + 2*(64746 | x)", 16)]
        for input_string, nbits in tests:
            input_ast = ast.parse(input_string)
            pattern_ast = ast.parse("(A ^ ~B) + 2*(A | B)")
            pat = pattern_matcher.PatternMatcher(input_ast, nbits)
            self.assertTrue(pat.visit(input_ast, pattern_ast))

    def test_real(self):
        'Tests inspirend from real events'
        pattern_string = "(A ^ ~B) + 2*(A | B)"
        tests = [("((4211719010 ^ (2937410391 * x))" +
                 "+ (2 * ((2937410391 * x) | 83248285)))")]
        for input_string in tests:
            self.generic_test_positive(input_string, pattern_string)

    def test_root(self):
        'Test with different types of roots'
        pattern_ast = ast.parse("A + B", mode='eval')
        input_ast = ast.parse("x + y", mode='eval')
        pat = pattern_matcher.PatternMatcher(input_ast)
        self.assertTrue(pat.visit(input_ast, pattern_ast))


class TestPatternReplacement(unittest.TestCase):
    """
    Test PatternReplacement class.
    """

    def generic_test_replacement(self, tests, pattern, replacement):
        'Generic test for a list of input/output'
        for input_string, refstring in tests:
            input_ast = ast.parse(input_string)
            ref_ast = ast.parse(refstring)
            patt_ast = ast.parse(pattern)
            rep_ast = ast.parse(replacement)
            rep = pattern_matcher.PatternReplacement(patt_ast, input_ast,
                                                     rep_ast)
            input_ast = rep.visit(input_ast)
            self.assertTrue(asttools.Comparator().visit(input_ast, ref_ast))

    def test_simple(self):
        'Simple tests for replacement'
        pattern = "(A ^ ~B) + 2*(A | B)"
        replacement = "A + B - 1"
        tests = [("(x ^ ~y) + 2*(x | y)", "x + y - 1"),
                 ("(x ^ ~45) + (45 | x)*2", "x + 45 - 1"),
                 ("((a + 32) ^ ~(var*5)) + ((a + 32) | (var*5))*2",
                  "(a + 32) + (var*5) - 1"),
                 ("((g ^ 23) | (a*x + b))*2 + ((a*x + b) ^ (g ^ 232))",
                  "~(g ^ 232) + (a*x + b) - 1"),
                 ("((g + 45) | (12 & n))*2 + ((-g - 46) ^ (12 & n))",
                  "(g + 45) + (12 & n) - 1")]
        self.generic_test_replacement(tests, pattern, replacement)

    def test_fcts(self):
        'Tests with pattern containing a function'
        pattern = 'max12(A) + 1'
        replacement = 'g(A)'
        tests = [('max12(x) + 1', 'g(x)'),
                 ('max12(56*y - 12) + 1', 'g(56*y - 12)')]
        self.generic_test_replacement(tests, pattern, replacement)
        pattern = 'bv64(0)'
        replacement = '0'
        tests = [('x + bv64(0)', 'x + 0')]
        self.generic_test_replacement(tests, pattern, replacement)

    def test_associativity(self):
        'Simple tests for associativity'
        pattern = "3*A + 2*B"
        replacement = "B"
        tests = [("2*x + 3*y", "x"), ("2*x + y + 3*g", "x + y")]
        for input_string, refstring in tests:
            ref_ast = ast.parse(refstring, mode="eval").body
            output_ast = pattern_matcher.replace(input_string, pattern,
                                                 replacement)
            self.assertTrue(asttools.Comparator().visit(output_ast, ref_ast))

    def test_flattened(self):
        'Test on flattened ast'
        patt_string = "A + 2*B + 3*C"
        rep_string = "A"
        test_pos = "3*z + x + 2*y"
        ref_ast = ast.parse("x", mode='eval').body
        output_ast = pattern_matcher.replace(test_pos, patt_string, rep_string)
        self.assertTrue(asttools.Comparator().visit(output_ast, ref_ast))

        # only ADD nodes are flattened right now, this is for code
        # coverage
        test_neg = ast.parse("3*z ^ x ^ 2*y")
        test_neg = Flattening().visit(test_neg)
        patt_ast = ast.parse("A + 3*z")
        patt_ast = Flattening().visit(patt_ast)
        rep_ast = ast.parse(rep_string)
        ref_ast = ast.parse("3*z ^ x ^ 2*y")
        ref_ast = Flattening().visit(ref_ast)
        rep = pattern_matcher.PatternReplacement(patt_ast, test_neg, rep_ast)
        output_ast = rep.visit(test_neg)
        self.assertTrue(asttools.Comparator().visit(output_ast, ref_ast))

    def test_real(self):
        'Tests inspired from real events'
        pattern = "(A ^ ~B) + 2*(A | B)"
        replacement = "A + B - 1"
        tests = [(("(4211719010 ^ 2937410391*x) +" +
                   "2*(2937410391*x | 83248285) + 4064867995"),
                  "((((2937410391 * x) + 83248285) - 1) + 4064867995)")]
        self.generic_test_replacement(tests, pattern, replacement)

    def test_root(self):
        'Test with different types of roots'
        patt_ast = ast.parse("A + B", mode='eval')
        input_ast = ast.parse("x + y", mode='eval')
        ref_ast = ast.parse("89", mode='eval')
        rep_ast = ast.parse("89", mode='eval')
        rep = pattern_matcher.PatternReplacement(patt_ast, input_ast, rep_ast)
        input_ast = rep.visit(input_ast)
        self.assertTrue(asttools.Comparator().visit(input_ast, ref_ast))


if __name__ == '__main__':
    unittest.main()
