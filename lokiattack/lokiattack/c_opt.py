from custom_architectures import *
from helper import *
from miasm.analysis.data_flow import PropagateThroughExprId as PropExpr, \
    PropagateExprIntThroughExprId as PropInt, PropagateThroughExprMem as PropMem
from miasm.analysis.simplifier import IRCFGSimplifierSSA, IRCFGSimplifierCommon


# Custom propagation hook. Parameterizable by function attributes:
#
# - `do_propagate`: Whether to perform any propagation at all.
# - `avoid`: Register versions that should not be propagated into.
# - `original`: The original function to fallback into.
def custom_propagation_allowed_expr(self, ssa, to_replace, node_a, node_b):
    # TODO: Make decision based on `.instr` that is propagated into -- requires
    # access to AssignBlock though.
    if not custom_propagation_allowed_expr.do_propagate:
        return False

    if isinstance(node_b.var, ExprId) and \
            node_b.var in custom_propagation_allowed_expr.avoid:
        return False

    return custom_propagation_allowed_expr.original(self, ssa, to_replace,
                                                    node_a, node_b)


def custom_propagation_allowed_int(_self, _ssa, _to_replace, _node_a, _node_b):
    return False


def custom_propagate_mem(_self, _ssa, _head, _max_expr_depth=None):
    return False


def c_opt_soft(arch, cfg, location, do_propagate=False, ssa_form=False):
    # Append fake assignments to make sure important register effects are kept.
    fake_assignment_labels = append_assignments(arch, cfg)

    # Translate the CFG into SSA form.
    arch_ssa = SsaArchitecture(arch.loc_db)
    simplifier = IRCFGSimplifierSSA(arch_ssa)
    ssa = simplifier.ircfg_to_ssa(cfg, location)

    # Collect the latest versions of (out) registers whose effects should be
    # kept.
    versions = {arch.IRDst}
    for l in fake_assignment_labels:
        block = ssa.get_block(l)
        last_assign_block = block.assignblks[-1]
        versions.update(last_assign_block.keys())

    # Hook the function that decides on propagation for `ExprId` instances and
    # set the function attributes accordingly.
    #
    # Expression propagation may remove the correlation of IR instructions to
    # the native instructions that yielded said IR (there is no way to track
    # associated instructions across single expressions).
    custom_propagation_allowed_expr.do_propagate = do_propagate
    custom_propagation_allowed_expr.original = PropExpr.propagation_allowed
    custom_propagation_allowed_expr.avoid = versions

    PropExpr.propagation_allowed = custom_propagation_allowed_expr

    # Also disable propagation of integeprs, as this may kill vital register
    # initializations, as well as propagation through memory.
    original_propint = None
    original_propmem = None

    if not do_propagate:
        original_propint = PropInt.propagation_allowed
        original_propmem = PropInt.propagate

        PropInt.propagation_allowed = custom_propagation_allowed_int
        PropMem.propagate = custom_propagate_mem

    # Simplify the SSA CFG using the propagation options configured above.
    # cfg = simplifier.simplify(cfg, location)
    ssa = simplifier.do_simplify_loop(ssa, location)
    remove_assignments(arch, ssa.graph, versions)

    cfg = simplifier.ssa_to_unssa(ssa, location)

    cfg_simplifier = IRCFGSimplifierCommon(simplifier.ir_arch)
    cfg_simplifier.simplify(cfg, location)

    PropExpr.propagation_allowed = custom_propagation_allowed_expr.original

    if original_propint:
        PropInt.propagation_allowed = original_propint

    if original_propmem:
        PropMem.propagate = original_propmem

    if not ssa_form:
        drop_indices(cfg)

    return cfg


def c_opt_hard(arch, cfg, location):
    arch_ssa = SsaArchitecture(arch.loc_db)

    append_assignments(arch, cfg)

    simplifier = IRCFGSimplifierSSA(arch_ssa)
    simplifier.simplify(cfg, location)

    return cfg


def c_opt(arch, cfg, location, hard_mode=False):
    if hard_mode:
        cfg = c_opt_hard(arch, cfg, location)
    else:
        cfg = c_opt_soft(arch, cfg, location)

    return cfg
