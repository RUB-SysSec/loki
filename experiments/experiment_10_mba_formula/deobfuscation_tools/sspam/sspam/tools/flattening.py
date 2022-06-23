"""Module for flattening operators.

Flattening transforms a binary operator * into a n-ary operator such
that no operand is an operator *.
For example, +(a, +(b, c)) is transformed into +(a, b, c).

In our case, this is done by transforming a BinOp into a BoolOp, which
is not a node designed to do this, but this will work as long as the ast
is not compiled or unparsed.

The algorithm to flatten is custom, there might be something more
efficient or simple."""

import ast


class Flattening(ast.NodeTransformer):
    """
    Walk through the ast and flatten successions of associative
    operators (+, x, &, |, ^) and transform binary nodes in n-ary
    nodes.
    """

    def __init__(self, onlyop=None):
        'Init current operation and storage for flattened nodes and operands'
        self.current_flattening = ast.BinOp(None, None, None)
        self.flattened_op = {}
        self.onlyop = onlyop

    def child_visit(self, node):
        'To avoid interaction between child visit'
        self.current_flattening = ast.BinOp(None, None, None)
        node.left = self.visit(node.left)
        self.current_flattening = ast.BinOp(None, None, None)
        node.right = self.visit(node.right)
        return node

    def visit_BinOp(self, node):
        'Transforms BinOp into flattened BoolOp if possible'

        self.flattened_op.setdefault(node, [])
        if self.onlyop and type(node.op) != self.onlyop:
            return self.child_visit(node)
        if type(node.op) != type(self.current_flattening.op):
            if isinstance(node.op, (ast.Add, ast.Mult, ast.BitAnd,
                                    ast.BitOr, ast.BitXor)):
                cond1 = (isinstance(node.left, ast.BinOp)
                         and type(node.left.op) == type(node.op))
                cond2 = (isinstance(node.right, ast.BinOp)
                         and type(node.right.op) == type(node.op))
                if cond1 or cond2:
                    self.current_flattening = node
                    self.generic_visit(node)
                    if ((not isinstance(node.right, ast.BinOp)
                         or type(node.right.op) != type(node.op))):
                        self.flattened_op[node].append(node.right)
                    if ((not isinstance(node.left, ast.BinOp)
                         or type(node.left.op) != type(node.op))):
                        self.flattened_op[node].append(node.left)
                else:
                    return self.child_visit(node)
            else:
                return self.child_visit(node)
        else:
            current_flattening = self.current_flattening
            node.left = self.visit(node.left)
            self.current_flattening = current_flattening
            node.right = self.visit(node.right)
            self.current_flattening = current_flattening
            for child in (node.left, node.right):
                cond = (isinstance(child, ast.BinOp)
                        and type(child.op) == type(node.op))
                if not cond:
                    self.flattened_op[self.current_flattening].append(child)

        if (self.flattened_op.get(node, None)
           and len(self.flattened_op[node]) > 1):
            return ast.BoolOp(node.op, self.flattened_op[node])
        return node

    def visit_UnaryOp(self, node):
        'UnaryOp are not flattened'
        self.current_flattening = ast.BinOp(None, None, None)
        return self.generic_visit(node)

    def visit_Call(self, node):
        'Calls interrupt the flattening'
        self.current_flattening = ast.BinOp(None, None, None)
        return self.generic_visit(node)


class Unflattening(ast.NodeTransformer):
    """
    Change flattened BoolOps back to regular BinOps.
    """

    def visit_BoolOp(self, node):
        'Build a serie of BinOp from BoolOp Children'

        self.generic_visit(node)
        rchildren = node.values[::-1]
        prev = ast.BinOp(rchildren[1], node.op, rchildren[0])

        for child in rchildren[2::]:
            prev = ast.BinOp(child, node.op, prev)

        return prev
