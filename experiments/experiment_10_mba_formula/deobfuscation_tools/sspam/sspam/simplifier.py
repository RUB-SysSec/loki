#!/usr/bin/python
"""Main simplification module.

Principal loop is in simplify() function:
  - pre-processing of asts
  - flattening of add (highly dependant of used rules in MBA
    obfuscation)
  - test each pattern if replacement is possible (does not break if
    replaced, so will try all patterns remaining)
  - bitwise simplification on XOR only (to be generalized)
  - basic constant folding
  - arithmetic simplification
  - pass to compute constant values according to the current modulus
"""

import ast
from astunparse import unparse
from copy import deepcopy
import os.path

from sspam.tools import asttools
from sspam.tools.flattening import Flattening, Unflattening
from sspam import pattern_matcher
from sspam.pre_processing import all_preprocessings
from sspam.pre_processing import NotToInv
from sspam import arithm_simpl


# list of known patterns and their replacements
DEFAULT_RULES = [("(A ^ ~B) + 2*(A | B)", "A + B - 1"),
                 ("(A | B) - (A & ~B)", "B"),
                 ("- (A ^ ~B) - 2*(A | B)", "-A - B + 1"),
                 ("A + B + 1 + (~A | ~B)", "(A | B)"),
                 ("A - B + (~(2*A) & 2*B)", "A ^ B"),
                 ("- A -(~(2*A) & 2*B)", "- (A ^ B) - B"),
                 # ("A + (~(2*A) & 2*B)", "(A ^ B) + B"),
                 ("-B + (~(2*A) & 2*B)", "(A ^ B) - A"),
                 ("-B + 2*(~A & B)", "(A ^ B) - A"),
                 ("A - B + 2*(~A & B)", "(A ^ B)"),
                 ("(A & B) + (A | B)", "A + B"),
                 ("(A ^ B) + 2*(A & B)", "A + B"),
                 ("A + B - 2*(A & B)", "(A ^ B)"),
                 ("- A - B + 2*(A | B)", "(A ^ B)"),
                 ("A + B - (A | B)", "A & B"),
                 ("(A & B) - (~A | B)", "A + 1"),
                 ("(A | B) - (A & B)", "A ^ B"),
                 ("-B + (2*(~A) & 2*B)", "(A ^ B) - A"),
                 ("-2*(~A & B) + B", "- (A ^ B) + A"),
                 ("A + B + (~A & ~B)", "(A & B) - 1"),
                 ("A + B + 2*(~A | ~B)", "(A ^ B) - 2"),
                 # makes test_my_mba.py fail if higher in the list
                 ("((2*A + 1) & 2*B)", "(2*A & 2*B)"),
                 ("(0 | A)", "A")]


DEBUG = False


class Simplifier(ast.NodeTransformer):
    """
    Simplifies a succession of assignments.
    For each assignment, simplify the value with :
    - replacing known variables
    - pattern matching
    - arithmetic simplification with z3
    - updating variable value for further replacement
    """

    def __init__(self, nbits, rules_list=DEFAULT_RULES):
        'Init context : correspondance between variables and values'
        # pylint: disable=dangerous-default-value
        self.context = {}
        self.nbits = nbits

        self.patterns = []
        for pattern, replace in rules_list:
            patt_ast = ast.parse(pattern, mode="eval").body
            patt_ast = all_preprocessings(patt_ast, self.nbits)
            patt_ast = Flattening(ast.Add).visit(patt_ast)
            rep_ast = ast.parse(replace, mode="eval").body
            self.patterns.append((patt_ast, rep_ast))

    def simplify(self, expr_ast, nbits):
        'Apply pattern matching and arithmetic simplification'
        expr_ast = arithm_simpl.run(expr_ast, nbits)
        expr_ast = asttools.GetConstMod(self.nbits).visit(expr_ast)
        if DEBUG:
            print("arithm simpl: ")
            print(unparse(expr_ast))
        if DEBUG:
            print("before matching: ")
            print(unparse(expr_ast))
        expr_ast = all_preprocessings(expr_ast, self.nbits)
        # only flattening ADD nodes because of traditionnal MBA patterns
        expr_ast = Flattening(ast.Add).visit(expr_ast)
        for pattern, repl in self.patterns:
            rep = pattern_matcher.PatternReplacement(pattern, expr_ast, repl)
            new_ast = rep.visit(deepcopy(expr_ast))
            if not asttools.Comparator().visit(new_ast, expr_ast):
                if DEBUG:
                    print("replaced! ")
                    dispat = deepcopy(pattern)
                    dispat = Unflattening().visit(dispat)
                    print("pattern:  ", unparse(dispat))
                    disnew = deepcopy(new_ast)
                    disnew = Unflattening().visit(disnew)
                    print("after:    ", unparse(disnew))
                expr_ast = new_ast
                break
        # bitwise simplification: this is a ugly hack, should be
        # "generalized"
        expr_ast = Flattening(ast.BitXor).visit(expr_ast)
        expr_ast = asttools.ConstFolding(expr_ast, self.nbits).visit(expr_ast)
        expr_ast = Unflattening().visit(expr_ast)
        if DEBUG:
            print("after PM: ")
            print(unparse(expr_ast))
        return expr_ast

    def loop_simplify(self, node):
        'Simplifying loop to reach fixpoint'
        old_value = deepcopy(node.value)
        old_value = Flattening().visit(old_value)
        node.value = self.simplify(node.value, self.nbits)
        copyvalue = deepcopy(node.value)
        copyvalue = Flattening().visit(copyvalue)
        # simplify until fixpoint is reached
        while not asttools.Comparator().visit(old_value, copyvalue):
            old_value = deepcopy(node.value)
            node.value = self.simplify(node.value, self.nbits)
            copyvalue = deepcopy(node.value)
            if len(unparse(copyvalue)) > len(unparse(old_value)):
                node.value = deepcopy(old_value)
                break
            copyvalue = Flattening().visit(copyvalue)
            old_value = Flattening().visit(old_value)
            if asttools.Comparator().visit(old_value, copyvalue):
                old_value = deepcopy(node.value)
                node.value = NotToInv().visit(node.value)
                node.value = self.simplify(node.value, self.nbits)
                copyvalue = deepcopy(node.value)
                # discard if NotToInv increased the size
                if len(unparse(copyvalue)) >= len(unparse(old_value)):
                    node.value = deepcopy(old_value)
                    copyvalue = deepcopy(node.value)
                copyvalue = Flattening().visit(copyvalue)
                old_value = Flattening().visit(old_value)
            if DEBUG:
                print("-"*80)
        # final arithmetic simplification to clean output of matching
        node.value = arithm_simpl.run(node.value, self.nbits)
        asttools.GetConstMod(self.nbits).visit(node.value)
        if DEBUG:
            print("arithm simpl: ")
            print(unparse(node.value))
            print("-"*80)
        return node

    def visit_Assign(self, node):
        'Simplify value of assignment and update context'

        # use EvalPattern to replace known variables
        node.value = pattern_matcher.EvalPattern(
            self.context).visit(node.value)
        node = self.loop_simplify(node)
        for target in node.targets:
            self.context[target.id] = node.value
        return node

    def visit_Expr(self, node):
        'Simplify expression and replace it'
        return self.loop_simplify(node)


def simplify(expr, nbits=0, custom_rules=None, use_default=True):
    """
    Take an expression and an optionnal number of bits as input.

    Expression can be given on command line or as a file, and should
    be in cse form (you can use cse script from sspam.tools)

    If not precised, number of bits will be deduced from the highest
    constant of the expression if possible, else it will be 8.

    """

    if os.path.isfile(expr):
        expr_file = open(expr, 'r')
        expr_ast = ast.parse(expr_file.read())
    else:
        expr_ast = ast.parse(expr)

    nbits = nbits
    if not nbits:
        nbits = asttools.get_default_nbits(expr_ast)

    if not use_default:
        rules_list = custom_rules
    elif not custom_rules:
        rules_list = DEFAULT_RULES
    else:
        rules_list = DEFAULT_RULES + custom_rules
    expr_ast = Simplifier(nbits, rules_list).visit(expr_ast)
    return unparse(expr_ast).strip('\n')
