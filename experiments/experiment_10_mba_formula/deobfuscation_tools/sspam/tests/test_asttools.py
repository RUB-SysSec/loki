"""Tests for asttools module.

- TestGetIdentifiers
- TestGetSize
- TestGetConstExpr
- TestConstFolding
- TestReplaceBitwiseOp
- TestReplaceBitwiseFunctions
- TestGetConstMod
- TestComparator
"""
# pylint: disable=relative-import

import ast
import unittest

from sspam.tools import asttools
from sspam.tools.flattening import Flattening
import templates


class TestGetIdentifiers(unittest.TestCase):
    """
    Test ast visitor GetIdentifiers.
    """

    def generic_test(self, tests):
        'Generic test for GetIdentifiers class'
        geti = asttools.GetIdentifiers()
        for instring, varref, funref in tests:
            geti.reset()
            inast = ast.parse(instring)
            geti.visit(inast)
            self.assertEquals(geti.variables, varref)
            self.assertEquals(geti.functions, funref)

    def test_basics_vars(self):
        'Simple tests for variables of GetIdentifiers'
        tests = [("x", {"x"}, set()), ("3*(x & 45) + x", {"x"}, set()),
                 ("x + 2*y", {"y", "x"}, set()),
                 ("bla - azerty + 2*(azerty + bla)", {"azerty", "bla"}, set())]
        self.generic_test(tests)

    def test_novariable(self):
        'Test when there is no variable'
        self.generic_test([('(3 + 34)*2', set(), set())])

    def test_basics_funs(self):
        'Simple tests for functions of GetIdentifiers'
        tests = [("a()", set(), {"a"}),
                 ("foo(a, b, c)", {'a', 'b', 'c'}, {'foo'})]
        self.generic_test(tests)


class TestGetSize(templates.AstVisitorCase):
    """
    Test ast visitor GetSize.
    """

    def test_basics(self):
        'Simple tests for GetSize'
        corresp = [("x", 0), ("x & 3", 2), ("x - 5", 4), ("x + 250", 8),
                   ("x*(-0x1325)", 16),
                   ("0xFFFFFFFE*x", 32), ("(0x123456789876543 | x) + 12", 64)]
        self.generic_AstVisitorTest(corresp, asttools.GetSize())


class TestGetConstExpr(templates.AstVisitorCase):
    """
    Test ast visitor GetConstExpr.
    """

    def test_GetConstExpr(self):
        'Simple tests for GetConstExpr'
        hooks = asttools.apply_hooks()
        corresp = [("3", set([ast.Num(3)])),
                   ("2 + 456", set([ast.Num(2),
                                    ast.Num(456),
                                    ast.BinOp(ast.Num(2), ast.Add(),
                                              ast.Num(456))])),
                   ("(3 + x) + 45", set([ast.Num(3), ast.Num(45)])),
                   (("x + y"), set())]
        self.generic_AstVisitorTest(corresp, asttools.GetConstExpr())
        asttools.restore_hooks(hooks)


class TestConstFolding(unittest.TestCase):
    """
    Test constant folding transformer.
    """

    def generic_ConstFolding(self, origstring, refstring, nbits, lvl=False):
        'Generic test for ConstFolding transformer'
        orig = ast.parse(origstring)
        ref = ast.parse(refstring)
        if lvl:
            orig = Flattening().visit(orig)
            ref = Flattening().visit(orig)
        orig = asttools.ConstFolding(orig, nbits).visit(orig)
        self.assertTrue(asttools.Comparator().visit(orig, ref))

    def test_basics(self):
        'Simple tests for ConstFolding'
        corresp = {"45 + 2": ["47", 8], "(3 + 2 + x)": ["(5 + x)", 16],
                   "2*230": ["204", 8], "2 - 4": ["254", 8],
                   "- (3*45)": ["4294967161", 32],
                   "(3 + x)*2 + 4": ["(3 + x)*2 + 4", 64]}
        for origstring, [refstring, nbits] in corresp.iteritems():
            self.generic_ConstFolding(origstring, refstring, nbits)

    def test_flattened_ast(self):
        'Simple tests for ConstFolding on custom BoolOps'
        corresp = {"(x + 3) + 2": ["x + 5", 8],
                   "((x ^ 14) ^ 234) ^ 48": ["x ^ 212", 8],
                   "42*34*y*z": ["1428*y*z", 16]}
        for origstring, [refstring, nbits] in corresp.iteritems():
            self.generic_ConstFolding(origstring, refstring, nbits, True)


class TestReplaceBitWiseOp(templates.AstCompCase):
    """
    Test behaviour of ast transformer ReplaceBitwiseOp.
    """

    def test_basics(self):
        'Simple tests for ReplaceBitwiseOp'
        corresp = [("x ^ y", "mxor(x, y)"), ("x & y", "mand(x, y)"),
                   ("x | y", "mor(x,y)"), ("(x ^ y) & 45",
                                           "mand(mxor(x,y), 45)"),
                   ("~x", "mnot(x)"), ("x + y", "x + y"),
                   ("(x & 3)*2 + ~(x - 3)", "mand(x, 3)*2 + mnot(x - 3)")]
        self.generic_AstCompTest(corresp, asttools.ReplaceBitwiseOp())


class TestReplaceBitwiseFunctions(templates.AstCompCase):
    """
    Test ast transformer class ReplaceBitwiseFunction.
    """

    def test_basics(self):
        'Simple tests for ReplaceBitwiseFunctions'
        corresp = [("mand(x, y)", "x & y"), ("mor(x, y)", "x | y"),
                   ("mxor(x ,y)", "x ^ y"), ("mnot(x)", "~x"),
                   ("mand(mor(x, 45), y) + 3", "((x | 45) & y) + 3")]
        self.generic_AstCompTest(corresp, asttools.ReplaceBitwiseFunctions())


class TestGetConstMod(templates.AstCompCase):
    """
    Test GetContMod.
    """

    def test_basics(self):
        'Simple tests for GetConstMod'
        corresp = {"34": ["2", 4], "356 + x": ["100 + x", 8],
                   "75901*y + 456": ["10365*y + 456", 16]}
        for origstring, [refstring, nbits] in corresp.iteritems():
            transformer = asttools.GetConstMod(nbits)
            self.generic_AstCompTest(origstring, refstring, transformer)


class TestComparator(unittest.TestCase):
    """
    Some tests for comparator because it's used in a lot in other tests.
    """

    def test_comp(self):
        'Basic tests for comparison'
        comp = asttools.Comparator()

        add_a = ast.parse('x + y')
        add_b = ast.parse('x + y')
        self.assertTrue(comp.visit(add_a, add_b))
        add_c = ast.parse('y + x')
        self.assertTrue(comp.visit(add_a, add_c))

        sub_a = ast.parse('x - y')
        self.assertFalse(comp.visit(add_a, sub_a))
        sub_b = ast.parse('y - x')
        self.assertFalse(comp.visit(sub_a, sub_b))

        expr_a = ast.parse('2*(x & y) + ((a - 3) ^ 45)')
        expr_b = ast.parse('2*(x & y) + ((a - 3) ^ 45)')
        self.assertTrue(comp.visit(expr_a, expr_b))
        expr_c = ast.parse('2*(y & x) + (45 ^ (a - 3))')
        self.assertTrue(comp.visit(expr_a, expr_c))
        expr_d = ast.parse('3*(y & x) + (45 ^ (a - 3))')
        self.assertFalse(comp.visit(expr_b, expr_d))

        expr_a = ast.parse('(3*x) + 57 - (x | (-2))')
        expr_b = ast.parse('3*x + 57 - (x | (-2))')
        self.assertTrue(comp.visit(expr_a, expr_b))

    def test_onBoolOp(self):
        'Tests on BoolOp'

        expr_a = ast.BoolOp(ast.Add(), [ast.Num(1), ast.Num(2), ast.Num(3)])
        expr_b = ast.BoolOp(ast.Add(), [ast.Num(3), ast.Num(2), ast.Num(1)])
        self.assertTrue(asttools.Comparator().visit(expr_a, expr_b))

        expr_a = ast.BoolOp(ast.Add, [ast.Num(1), ast.BoolOp(ast.Mult(),
                                                             [ast.Num(5),
                                                              ast.Num(6)]),
                                      ast.Num(4)])
        expr_b = ast.BoolOp(ast.Add, [ast.BoolOp(ast.Mult(), [ast.Num(6),
                                                              ast.Num(5)]),
                                      ast.Num(4),
                                      ast.Num(1)])
        self.assertTrue(asttools.Comparator().visit(expr_a, expr_b))


if __name__ == '__main__':
    unittest.main()
