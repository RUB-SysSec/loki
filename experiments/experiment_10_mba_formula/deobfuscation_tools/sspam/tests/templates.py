"""Templates of test on ast used in several tests
"""

import ast
import unittest

from sspam import pattern_matcher, simplifier
from sspam.tools import asttools


class AstCompCase(unittest.TestCase):
    """
    Generic method to compare obfuscated ast and original ast.
    """

    def generic_AstCompTest(self, *args):
        """Args: (tests, transformer) with tests a list,
        or (input_string, refstring, transformer)"""

        if len(args) != 2 and len(args) != 3:
            raise Exception("generic_AstTest should be " +
                            "called with 3 or 4 arguments")
        if len(args) == 2:
            tests = args[0]
            transformer = args[1]
        else:
            tests = [(args[0], args[1])]
            transformer = args[2]
        for origstring, refstring in tests:
            orig = ast.parse(origstring)
            ref = ast.parse(refstring)
            orig = transformer.visit(orig)
            self.assertTrue(asttools.Comparator().visit(orig, ref))


class AstVisitorCase(unittest.TestCase):
    """
    Generic method to compare result of ast visitor.
    """

    def generic_AstVisitorTest(self, *args):
        'Generic test for comparison of NodeVisitor results'

        if len(args) != 2 and len(args) != 3:
            print args
            raise Exception("generic_AstVisitorTest should be " +
                            "called with 3 or 4 arguments")

        if len(args) == 2:
            tests = args[0]
            visitor = args[1]
        else:
            tests = [(args[0], args[1])]
            visitor = args[2]
        for refstring, results in tests:
            ref = ast.parse(refstring)
            visitor.visit(ref)
            out = visitor.result
            self.assertEquals(out, results)
            visitor.reset()


class PatternMatcherTest(unittest.TestCase):
    """
    Generic class for tests on pattern matcher (short and long)
    """

    def generic_test_positive(self, input_string, patt_string, preproc=False):
        'Generic test for positive matching'
        input_ast = ast.parse(input_string)
        pattern_ast = ast.parse(patt_string)
        if not preproc:
            pat = pattern_matcher.PatternMatcher(input_ast)
            self.assertTrue(pat.visit(input_ast, pattern_ast))
        self.assertTrue(pattern_matcher.match(input_string, patt_string))

    def generic_test_negative(self, input_string, patt_string, preproc=False):
        'Generic test for negative matching'
        input_ast = ast.parse(input_string)
        pattern_ast = ast.parse(patt_string)
        if not preproc:
            pat = pattern_matcher.PatternMatcher(input_ast)
            self.assertFalse(pat.visit(input_ast, pattern_ast))
        self.assertFalse(pattern_matcher.match(input_string, patt_string))


class SimplifierTest(unittest.TestCase):
    """
    Generic class for tests on simplifier (short and long)
    """

    def generic_test(self, expr, refstring, nbits=0):
        'Generic test for simplifier script'
        output_string = simplifier.simplify(expr, nbits)
        output = ast.parse(output_string)
        ref = ast.parse(refstring)
        self.assertTrue(asttools.Comparator().visit(output, ref))
