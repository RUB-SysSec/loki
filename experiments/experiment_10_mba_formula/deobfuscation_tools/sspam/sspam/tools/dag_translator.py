"""
Script used to transform expressions into DAG representation.
Input must be a python file or an inlined expression containing an
expression (not an assignment).

Main function applies to input:
- leveling of associative operators;
- common subexpression search (custom or sympy);
- conversion into dot graph and optionnal drawing of the graph.

"""
import sys
import ast
import pygraphviz
import argparse
import random
import time
import os.path
from copy import deepcopy


from sspam.tools import asttools
from sspam.tools import cse
from sspam.tools.flattening import Flattening, Unflattening


CORRESP = {ast.Add: '+', ast.Sub: '-', ast.Mult: '&#215;', ast.USub: '-',
           ast.BitAnd: '&#8743;', ast.BitOr: '&#8744;', ast.BitXor: '&#8853;',
           ast.LShift: '<<', ast.RShift: '>>',
           ast.Mod: '%', ast.Invert: "&#172;"}

ARITHM = {ast.Add, ast.Sub, ast.Mult, ast.USub}
BOOL = {ast.BitAnd, ast.BitOr, ast.BitXor, ast.Invert}


class DAGTranslator(ast.NodeVisitor):
    """
    Create a pygraphviz graph from an ast.
    The ast must contain a list of assignments in a CSE form.
    """

    def __init__(self, input_ast):
        'Init graph, subexpr list, set of ids (for op node) and variables'
        self.graph = pygraphviz.AGraph(directed=True, rankdir='TB')
        self.subexpr = {}
        self.variables = set()
        # numeric value of expression can't be used as ids
        numsgather = asttools.GetNums()
        numsgather.visit(input_ast)
        self.ids = numsgather.result
        self.alternation = 0

    @staticmethod
    def check_alternation(node1, node2):
        'Check if we have a arithmetic / boolean alternance'
        types = set((type(node1), type(node2)))
        nodetype = set((ast.BinOp, ast.UnaryOp, ast.BoolOp))
        if not types.issubset(nodetype):
            return False
        types_op = set((type(node1.op), type(node2.op)))
        # check that both operators are of different types
        if not (types_op.issubset(ARITHM) or types_op.issubset(BOOL)):
            return True
        return False

    def visit_Assign(self, node):
        'Associate subgraph to variable'
        subgraph = self.visit(node.value)
        self.subexpr[node.targets[0].id] = subgraph

    def visit_BinOp(self, node):
        'Choose random id for node and visit left and right'
        opid = random.randint(0, 9999999999)
        while opid in self.ids:
            opid = random.randint(0, 9999999999)
        self.ids.add(opid)
        self.graph.add_node(opid, label=CORRESP[type(node.op)])
        left = self.visit(node.left)
        right = self.visit(node.right)

        self.graph.add_edge(opid, left)
        if self.check_alternation(node, node.left):
            self.alternation += 1
        self.graph.add_edge(opid, right)
        if self.check_alternation(node, node.right):
            self.alternation += 1
        return opid

    def visit_BoolOp(self, node):
        'Choose random id for node and visit all children'
        opid = random.randint(0, 9999999999)
        while opid in self.ids:
            opid = random.randint(0, 9999999999)
        self.ids.add(opid)
        self.graph.add_node(opid, label=CORRESP[type(node.op)])
        for child in node.values:
            child = self.visit(child)
            self.graph.add_edge(opid, child)
            if self.check_alternation(node, child):
                self.alternation += 1
        return opid

    def visit_UnaryOp(self, node):
        'Choose random id for node and visit operand'
        opid = random.randint(0, 9999999999)
        while opid in self.ids:
            opid = random.randint(0, 9999999999)
        self.ids.add(opid)
        self.graph.add_node(opid, label=CORRESP[type(node.op)])
        operand = self.visit(node.operand)
        self.graph.add_edge(opid, operand)
        self.check_alternation(node, node.operand)
        return opid

    def visit_Name(self, node):
        'Create node if variable, else replace by corresponding value'
        if node.id in self.subexpr.keys():
            return self.subexpr[node.id]
        if node.id not in self.graph:
            self.graph.add_node(node.id)
            self.variables.add(node.id)
        return node.id

    def visit_Num(self, node):
        'Create node if not already existing'
        if node.n not in self.graph:
            self.graph.add_node(node.n)
            self.variables.add(node.n)
        return node.n


def get_metrics(expr_ast):
    'Return number of nodes and MBA alternation of DAG'
    input_ast = deepcopy(expr_ast)
    input_ast = Unflattening().visit(input_ast)
    input_ast = cse.apply_cse(input_ast)[1]
    visitor = DAGTranslator(input_ast)
    visitor.visit(input_ast)
    graph = visitor.graph
    graph.subgraph(list(visitor.variables), rank="same")
    return len(graph), visitor.alternation


def main(argv):
    'Parse option and arguments and translate AST to DOT graph'
    random.seed(time.time())
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str,
                        help="python file containing expression to translate" +
                        "OR directly the python expression")
    parser.add_argument("-d", "--draw", action="store_true",
                        help="draw the corresponding graph")
    parser.add_argument("--no-cse", action="store_true",
                        help="deactivate cse")
    parser.add_argument("--no-file", action="store_true",
                        help="deactivate writing in a output file" +
                        " (useful for tests)")

    args = parser.parse_args(argv)

    if os.path.isfile(args.input):
        input_file = open(args.input, 'r')
        filename = args.input[:-3]
        input_ast = ast.parse(input_file.read())
    else:
        # if input is not a file, then it's considered as an expression
        input_ast = ast.parse(args.input)
        filename = "your_output_%d" % random.randint(0, 99)

    if not args.no_cse:
        input_ast = cse.apply_cse(input_ast)[1]

    input_ast = Flattening().visit(input_ast)
    visitor = DAGTranslator(input_ast)
    visitor.visit(input_ast)
    graph = visitor.graph
    graph.subgraph(list(visitor.variables), rank="same")

    if not args.no_file:
        graph.write("%s.dot" % filename)

    if args.draw:
        graph.layout(prog="dot")
        graph.draw("%s.pdf" % filename)

    print("Number of nodes:", len(graph))
    print("Alternation of types:", visitor.alternation)
    print("your output is named:", filename)
    return graph


if __name__ == "__main__":
    main(sys.argv[1:])
