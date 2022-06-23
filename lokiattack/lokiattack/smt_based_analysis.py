from miasm.expression.expression import Expr
from miasm.ir.translators.z3_ir import TranslatorZ3


def _is_semantically_equivalent(e1, e2):
    solver = Solver()
    solver.add(e1 != e2)
    return solver.check() == unsat


def is_semantically_equivalent(e1, e2):
    """
    @param e1: miasm or BitVec expression
    @param e2: miasm or BitVec expression
    
    Wrapper for _is_semantically_equivalent which transformes
    a miasm expression e1 into a z3 expression.
    """
    translator = TranslatorZ3()

    if isinstance(e1, Expr):
        e1 = translator.from_expr(e1)

    if isinstance(e2, Expr):
        e2 = translator.from_expr(e2)

    return _is_semantically_equivalent(e1, e2)
