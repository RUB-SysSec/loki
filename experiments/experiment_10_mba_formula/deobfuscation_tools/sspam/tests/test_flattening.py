"""Tests for flattening module.
"""

import ast
import unittest
import astunparse

from sspam import pre_processing
from sspam.tools.asttools import Comparator
from sspam.tools.flattening import Flattening, Unflattening


class TestFlattening(unittest.TestCase):
    """
    Test that flattening produce expected ast.
    """

    def generic_flattening(self, refstring_list, result):
        'Test matching of flattened AST and ref AST'
        for refstring in refstring_list:
            ref = ast.parse(refstring, mode="eval").body
            ref = Flattening().visit(ref)
            self.assertTrue(Comparator().visit(ref, result))

    def test_basics(self):
        'Simple tests with matching of AST'
        corresp = [(["a + b + c", "a + (b + c)", "b + c + a"],
                    ast.BoolOp(ast.Add(),
                               [ast.Name('a', ast.Load()),
                                ast.Name('b', ast.Load()),
                                ast.Name('c', ast.Load())])),
                   (["a + b + c + d", "(a + b) + (c + d)",
                     "a + (b + c + d)", "a + (b + (c + d))"],
                    ast.BoolOp(ast.Add(),
                               [ast.Name('a', ast.Load()),
                                ast.Name('b', ast.Load()),
                                ast.Name('c', ast.Load()),
                                ast.Name('d', ast.Load())])),
                   (["a + b + c*d", "a + c*d + b"],
                    ast.BoolOp(ast.Add(),
                               [ast.Name('a', ast.Load()),
                                ast.Name('b', ast.Load()),
                                ast.BinOp(ast.Name('c', ast.Load()),
                                          ast.Mult(),
                                          ast.Name('d', ast.Load()))])),
                   (["a*b*c"],
                    ast.BoolOp(ast.Mult(),
                               [ast.Name('a', ast.Load()),
                                ast.Name('b', ast.Load()),
                                ast.Name('c', ast.Load())])),
                   (["a + c*d*e"],
                    ast.BinOp(ast.Name('a', ast.Load()), ast.Add(),
                              ast.BoolOp(ast.Mult(),
                                         [ast.Name('c', ast.Load()),
                                          ast.Name('d', ast.Load()),
                                          ast.Name('e', ast.Load())]))),
                   (["a + b + c + c*d", "a + c*d + b + c"],
                    ast.BoolOp(ast.Add(),
                               [ast.Name('a', ast.Load()),
                                ast.Name('b', ast.Load()),
                                ast.Name('c', ast.Load()),
                                ast.BinOp(ast.Name('c', ast.Load()),
                                          ast.Mult(),
                                          ast.Name('d', ast.Load()))])),
                   (["a + b + c*d*e", "a + c*d*e + b", "b + e*c*d + a"],
                    ast.BoolOp(ast.Add(),
                               [ast.Name('a', ast.Load()),
                                ast.Name('b', ast.Load()),
                                ast.BoolOp(ast.Mult(),
                                           [ast.Name('c', ast.Load()),
                                            ast.Name('d', ast.Load()),
                                            ast.Name('e', ast.Load())])])),
                   (["a + c*d*e + b + c"],
                    ast.BoolOp(ast.Add(),
                               [ast.Name('a', ast.Load()),
                                ast.Name('b', ast.Load()),
                                ast.Name('c', ast.Load()),
                                ast.BoolOp(ast.Mult(),
                                           [ast.Name('c', ast.Load()),
                                            ast.Name('d', ast.Load()),
                                            ast.Name('e', ast.Load())])]))]
        for refstring, result in corresp:
            self.generic_flattening(refstring, result)

    def test_astform(self):
        'Tests with different types of ast'
        t1 = ast.parse("1 + 2 + 3", mode="eval").body
        t1_ref = ast.BoolOp(ast.Add(), [ast.Num(1), ast.Num(2), ast.Num(3)])
        t2 = ast.parse("1 + 2 + 3", mode="eval")
        t3 = ast.parse("1 + 2 + 3").body[0]
        tests = [(t1, t1_ref), (t2, ast.Expression(t1_ref)),
                 (t3, ast.Expr(t1_ref))]
        for test, ref in tests:
            ltest = Flattening().visit(test)
            self.assertTrue(Comparator().visit(ltest, ref))

    def test_afterSubMult(self):
        'Tests after SubToMult pre-processing'

        tests = [("1 + 2 - 3", ast.BoolOp(ast.Add(), [ast.Num(1), ast.Num(2),
                                                      ast.BinOp(ast.Num(-1),
                                                                ast.Mult(),
                                                                ast.Num(3))])),
                 ("1 + 2 - 3 + 4", ast.BoolOp(ast.Add(),
                                              [ast.Num(1),
                                               ast.Num(2),
                                               ast.BinOp(ast.Num(-1),
                                                         ast.Mult(),
                                                         ast.Num(3)),
                                               ast.Num(4)])),
                 ("(1 + 2) - (3 + 4)",
                  ast.BoolOp(ast.Add(),
                             [ast.Num(1), ast.Num(2),
                              ast.BinOp(ast.Num(-1), ast.Mult(),
                                        ast.BinOp(ast.Num(3), ast.Add(),
                                                  ast.Num(4)))]))]
        for teststring, ref_ast in tests:
            test_ast = ast.parse(teststring, mode="eval").body
            test_ast = pre_processing.all_preprocessings(test_ast)
            test_ast = Flattening(ast.Add).visit(test_ast)
            self.assertTrue(Comparator().visit(test_ast, ref_ast))

    def test_differentops(self):
        'Test with other types of operators'
        tests = [("(3 & 5 & 6)",
                  ast.BoolOp(ast.BitAnd(),
                             [ast.Num(3), ast.Num(5), ast.Num(6)])),
                 ("(1 ^ 2 ^ 3) - 4",
                  ast.BinOp(ast.BoolOp(ast.BitXor(),
                                       [ast.Num(1), ast.Num(2), ast.Num(3)]),
                            ast.Add(),
                            ast.BinOp(ast.Num(-1), ast.Mult(), ast.Num(4)))),
                 ("((1 + 2 + 3) & (4 + 5))",
                  ast.BinOp(ast.BoolOp(ast.Add(),
                                       [ast.Num(1), ast.Num(2), ast.Num(3)]),
                            ast.BitAnd(),
                            ast.BinOp(ast.Num(4), ast.Add(), ast.Num(5)))),
                 ("(1 & 2 & 3) - (4 & 5)",
                  ast.BinOp(ast.BoolOp(ast.BitAnd(),
                                       [ast.Num(1), ast.Num(2), ast.Num(3)]),
                            ast.Add(),
                            ast.BinOp(ast.Num(-1), ast.Mult(),
                                      ast.BinOp(ast.Num(4), ast.BitAnd(),
                                                ast.Num(5))))),
                 ("(1 & 2 & 3) << (4 & 5)",
                  ast.BinOp(ast.BoolOp(ast.BitAnd(),
                                       [ast.Num(1), ast.Num(2), ast.Num(3)]),
                            ast.LShift(),
                            ast.BinOp(ast.Num(4), ast.BitAnd(), ast.Num(5))))]
        for teststring, ref_ast in tests:
            test_ast = ast.parse(teststring, mode="eval").body
            test_ast = pre_processing.all_preprocessings(test_ast)
            test_ast = Flattening().visit(test_ast)
            self.assertTrue(Comparator().visit(test_ast, ref_ast))

    def test_withUnaryOp(self):
        'Test with UnaryOp involved'
        tests = [("5 + (-(6 + 2)) + 3",
                  ast.BoolOp(ast.Add(),
                             [ast.Num(5),
                              ast.UnaryOp(ast.USub(), ast.BinOp(ast.Num(6),
                                                                ast.Add(),
                                                                ast.Num(2))),
                              ast.Num(3)]))]
        for teststring, ref_ast in tests:
            test_ast = ast.parse(teststring, mode="eval").body
            test_ast = Flattening(ast.Add).visit(test_ast)
            self.assertTrue(Comparator().visit(test_ast, ref_ast))

    def test_with_funcs(self):
        'Tests with functions'
        tests = [
            ("f(1 + 1 + 1)",
             ast.Call(ast.Name('f', ast.Load()),
                      [ast.BoolOp(ast.Add(),
                                  [ast.Num(n) for n in [1, 1, 1]])],
                      [],
                      None,
                      None)),
            ("f(1 + 1 + g(2 + 2 + 2))",
             ast.Call(ast.Name('f', ast.Load()),
                      [ast.BoolOp(ast.Add(),
                                  [ast.Num(1),
                                   ast.Num(1),
                                   ast.Call(ast.Name('g', ast.Load()),
                                            [ast.BoolOp(ast.Add(),
                                                        [ast.Num(2),
                                                         ast.Num(2),
                                                            ast.Num(2)])],
                                            [],
                                            None,
                                            None)])],
                      [],
                      None,
                      None)),
            ("f(8) + (a + f(8)) + f(14)",
             ast.BoolOp(ast.Add(),
                        [ast.Call(ast.Name('f', ast.Load()),
                                  [ast.Num(8)], [], None, None),
                         ast.Name('a', ast.Load()),
                         ast.Call(ast.Name('f', ast.Load()),
                                  [ast.Num(8)], [], None, None),
                         ast.Call(ast.Name('f', ast.Load()),
                                  [ast.Num(14)], [], None, None)]))]
        for teststring, ref_ast in tests:
            test_ast = ast.parse(teststring, mode="eval").body
            test_ast = Flattening(ast.Add).visit(test_ast)
            self.assertTrue(Comparator().visit(test_ast, ref_ast))

    def test_noflattening(self):
        'Tests where nothing should be flattened'
        corresp = [(["a + b", "b + a"],
                   ast.BinOp(ast.Name('a', ast.Load()),
                             ast.Add(),
                             ast.Name('b', ast.Load()))),
                   (["c*d", "d*c"],
                    ast.BinOp(ast.Name('c', ast.Load()),
                              ast.Mult(),
                              ast.Name('d', ast.Load()))),
                   (["a + c*d", "d*c + a"],
                    ast.BinOp(ast.Name('a', ast.Load()), ast.Add(),
                              ast.BinOp(ast.Name('c', ast.Load()), ast.Mult(),
                                        ast.Name('d', ast.Load()))))]
        for refstring, result in corresp:
            self.generic_flattening(refstring, result)

    def test_unflattening(self):
        'Tests to see if unflattening is correct'

        tests = [("x + (3 + y)", "3 + (y + x)"),
                 ("x*(2*z)", "2*(z*x)"),
                 ("x + (y + (z*(5*var)))", "y + (5*(var*z) + x)")]

        for test, ref in tests:
            ref_ast = ast.parse(ref)
            ast_test = ast.parse(test)
            Flattening().visit(ast_test)
            Unflattening().visit(ast_test)
            self.assertTrue(Comparator().visit(ast_test, ref_ast))
            self.assertFalse('BoolOp' in astunparse.unparse(ast_test))


if __name__ == '__main__':
    unittest.main()
