"""Pre-processing module.

This module contains several pre-processing routines that can help
detect more patterns with PatternMatcher.

Classes included in this module are:
 - ShiftToMult: transforms all left shifts of a constant in
   multiplications
 - SubToMult: transforms subs operator into + (-1)*
 - NotToInv(): transforms ~x in -x - 1
 - RemoveUselessAnd: removes & 2^n if expression is on n bits
 - all_preprocessings: applies all preprocessing transformations
   designed for patterns
 - all_target_preprocessings: NotToInv() is not used for patterns
"""

import ast

from sspam.tools import asttools


class ShiftToMult(ast.NodeTransformer):
    """
    Transform all left shifts of a constant in multiplications.
    """

    def visit_BinOp(self, node):
        'Change left shifts into multiplications'

        if not isinstance(node.op, ast.LShift):
            return self.generic_visit(node)
        if isinstance(node.right, ast.Num):
            self.generic_visit(node)
            return ast.BinOp(node.left, ast.Mult(), ast.Num(2**(node.right.n)))
        return self.generic_visit(node)


class SubToMult(ast.NodeTransformer):
    """
    Subs are a pain in the ass. Let's change them to *(-1)
    """

    def __init__(self, nbits=0):
        self.nbits = nbits

    def visit_BinOp(self, node):
        'Change operator - to a *(-1)'

        self.generic_visit(node)
        if isinstance(node.op, ast.Sub):
            node.op = ast.Add()
            cond_mult = (isinstance(node.right, ast.BinOp) and
                         isinstance(node.right.op, ast.Mult))
            if cond_mult:
                if isinstance(node.right.left, ast.Num):
                    coeff = node.right.left
                    operand = node.right.right
                elif isinstance(node.right.right, ast.Num):
                    coeff = node.right.right
                    operand = node.right.left
                else:
                    node.right = ast.BinOp(ast.Num(-1), ast.Mult(), node.right)
                    return node
                # trying to "simplify" constant coeffs if possible
                if self.nbits:
                    if (-coeff.n) % 2**self.nbits == 1:
                        node.right = operand
                    else:
                        coeff.n = -coeff.n % 2**self.nbits
                else:
                    coeff.n = -coeff.n
            else:
                node.right = ast.BinOp(ast.Num(-1), ast.Mult(), node.right)
        return node

    def visit_UnaryOp(self, node):
        'Change -x to (-1)*x'
        self.generic_visit(node)
        if isinstance(node.op, ast.USub):
            ope = node.operand
            cond_mult = (isinstance(ope, ast.BinOp) and
                         isinstance(ope.op, ast.Mult))
            if cond_mult:
                if isinstance(ope.left, ast.Num):
                    node = ast.BinOp(ast.Num(-ope.left.n), ast.Mult(),
                                     ope.right)
                elif isinstance(ope.right, ast.Num):
                    node = ast.BinOp(ope.left, ast.Mult(),
                                     ast.Num(-ope.right.n))
                else:
                    node = ast.BinOp(ast.Num(-1), ast.Mult(), ope)
            else:
                node = ast.BinOp(ast.Num(-1), ast.Mult(), ope)
        return node


class NotToInv(ast.NodeTransformer):
    """
    Transform a (~X) in (- X - 1).
    """

    def visit_UnaryOp(self, node):
        'Change ~x to - x - 1'

        if isinstance(node.op, ast.Invert):
            return ast.BinOp(ast.UnaryOp(ast.USub(), node.operand),
                             ast.Add(),
                             ast.Num(-1))
        return self.generic_visit(node)


class RemoveUselessAnd(ast.NodeTransformer):
    """
    (A & 0xFF...FF) == A
    """

    def __init__(self, nbits):
        self.nbits = nbits

    def visit_BinOp(self, node):
        'Change (A & 2**self.nbits - 1) in A'
        if isinstance(node.op, ast.BitAnd):
            if isinstance(node.right, ast.Num):
                if node.right.n != (2**self.nbits - 1):
                    return self.generic_visit(node)
                return self.generic_visit(node.left)
            if isinstance(node.left, ast.Num):
                if node.left.n != (2**self.nbits - 1):
                    return self.generic_visit(node)
                return self.generic_visit(node.right)
        return self.generic_visit(node)


def all_preprocessings(asttarget, nbits=0):
    'Apply all pre-processing transforms'
    if not nbits:
        nbits = asttools.get_default_nbits(asttarget)
    asttarget = ShiftToMult().visit(asttarget)
    asttarget = SubToMult().visit(asttarget)
    asttarget = RemoveUselessAnd(nbits).visit(asttarget)
    ast.fix_missing_locations(asttarget)
    return asttarget
