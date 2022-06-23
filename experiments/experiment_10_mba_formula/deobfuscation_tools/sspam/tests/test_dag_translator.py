"""Tests for DAG translator.
"""

import ast
import pytest
import random


from sspam.tools import dag_translator
from sspam.tools.flattening import Flattening

#pylint: disable=anomalous-unicode-escape-in-string,invalid-name,no-member

testops = [
    ('a + b', """strict digraph {
\tgraph [rankdir=TB];
\tnode [label="\N"];
\t9607807567	 [label="+"];
\t9607807567 -> a;
\t9607807567 -> b;
}
"""),
    ('a & b', """strict digraph {
\tgraph [rankdir=TB];
\tnode [label="\N"];
\t9607807567	 [label="&#8743;"];
\t9607807567 -> a;
\t9607807567 -> b;
}
"""),
    ("~a", """strict digraph {
\tgraph [rankdir=TB];
\tnode [label="\N"];
\t9607807567	 [label="&#172;"];
\t9607807567 -> a;
}
""")
]


@pytest.mark.parametrize("expr_string, refgraph", testops)
def test_basicops(expr_string, refgraph):
    'Test if classic operators are correctly processed into DAG'
    random.seed(124)
    expr_ast = ast.parse(expr_string)
    visitor = dag_translator.DAGTranslator(expr_ast)
    visitor.visit(expr_ast)
    graph = visitor.graph
    assert str(graph.string()) == refgraph


testsharing = [
    ("a = (x + y)\nb = (a & 1) + a", """strict digraph {
\tgraph [rankdir=TB];
\tnode [label="\\N"];
\t5482553095\t [label="+"];
\t5482553095 -> x;
\t5482553095 -> y;
\t1770794909\t [label="+"];
\t1770794909 -> 5482553095;
\t9654901181\t [label="&#8743;"];
\t1770794909 -> 9654901181;
\t9654901181 -> 5482553095;
\t9654901181 -> 1;
}
"""),
    ("a = (x & y)\nb = 3 + 2*a\nc = a + b", """strict digraph {
\tgraph [rankdir=TB];
\tnode [label="\\N"];
\t4161890244\t [label="&#8743;"];
\t4161890244 -> x;
\t4161890244 -> y;
\t7875355434\t [label="+"];
\t7875355434 -> 3;
\t315895402\t [label="&#215;"];
\t7875355434 -> 315895402;
\t315895402 -> 4161890244;
\t315895402 -> 2;
\t1654751106\t [label="+"];
\t1654751106 -> 4161890244;
\t1654751106 -> 7875355434;
}
""")
]


@pytest.mark.parametrize("expr_string, refgraph", testsharing)
def test_sharing(expr_string, refgraph):
    'Test if multiple subexpressions are correctly shared'
    expr_ast = ast.parse(expr_string)
    visitor = dag_translator.DAGTranslator(expr_ast)
    visitor.visit(expr_ast)
    graph = visitor.graph
    assert str(graph.string()) == refgraph


testboolop = [
    ("a + b + c", """strict digraph {
\tgraph [rankdir=TB];
\tnode [label="\\N"];
\t9680462502\t [label="+"];
\t9680462502 -> a;
\t9680462502 -> b;
\t9680462502 -> c;
}
"""),
]


@pytest.mark.parametrize("expr_string, refgraph", testboolop)
def test_flattening(expr_string, refgraph):
    'Test if BoolOp are correctly processed'
    expr_ast = ast.parse(expr_string)
    expr_ast = Flattening().visit(expr_ast)
    visitor = dag_translator.DAGTranslator(expr_ast)
    visitor.visit(expr_ast)
    graph = visitor.graph
    assert str(graph.string()) == refgraph
