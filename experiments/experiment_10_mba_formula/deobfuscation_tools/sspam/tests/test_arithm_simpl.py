"""
Test for arithmetic simplifier module.

Right now this part is done by sympy, which we relatively trust.
"""

import unittest
import ast

from sspam import arithm_simpl
from sspam.tools import asttools


class TestArithSimplifier(unittest.TestCase):
    """
    Tests for arithm_simplifier function.
    """

    def generic_test(self, input_ast, ref_ast, nbits):
        'Generic test for arithmetic simplification'
        output_ast = arithm_simpl.run(input_ast, nbits)
        self.assertTrue(asttools.Comparator().visit(output_ast, ref_ast))

    def test_simple(self):
        'Some basics tests'

        nbits = 8
        tests = [("x", "x"), ("x + 3 - 3", "x"), ("x + x*y - x*y", "x"),
                 ("x + 45 + 243", "x + 32")]
        for input_string, ref_string in tests:
            input_ast = ast.parse(input_string, mode='eval')
            ref_ast = ast.parse(ref_string, mode='eval')
            self.generic_test(input_ast, ref_ast, nbits)
        # test with ast.Module
        for input_string, ref_string in tests:
            input_ast = ast.parse(input_string)
            ref_ast = ast.parse(ref_string)
            self.generic_test(input_ast, ref_ast, nbits)

    def test_withFunc(self):
        'Test simplification of arguments'

        nbits = 8
        tests = [("foo(x + x)", "foo(2*x)"), ("foo(x - x)", "foo(0)"),
                 ("foo(1 + 1)", "foo(2)"),
                 ("foo(x + 3*x + 45 - 4)", "foo(4*x + 41)"),
                 ("f(x + x + g(z + 3 + z) + x)", "f(3*x + g(2*z + 3))")]
        for input_string, ref_string in tests:
            input_ast = ast.parse(input_string, mode='eval')
            ref_ast = ast.parse(ref_string, mode='eval')
            self.generic_test(input_ast, ref_ast, nbits)


if __name__ == '__main__':
    unittest.main()
