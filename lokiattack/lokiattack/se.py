from collections import namedtuple
from typing import Dict

from miasm.analysis.binary import Container
from miasm.analysis.machine import Machine
from miasm.expression.simplifications import expr_simp_explicit
from miasm.ir.symbexec import SymbolicExecutionEngine

from .helper import *


Checkpoint = namedtuple("Checkpoint", "state succs path")
SeResultEntry = namedtuple("SeResultEntry", "path state")
OutputResultEntry = namedtuple("OutputResultEntry", "path output output_instr_offset")
SEContext = namedtuple("SEContext", "context_addr bytecode_addr x_val y_val c_val key_val")

OUTPUT = ExprId("output", 64)
X = ExprId("x", 64)
Y = ExprId("y", 64)
C = ExprId("c", 64)
KEY = ExprId("key", 64)


def symbolically_execute_path_alt(ira, ir_cfg, se_context, path):
    se, replacements = gen_se(ira, se_context)

    result = _symbolically_execute_path(ira, ir_cfg, path, se=se)
    result = SeResultEntry(path, result)

    return filter_output(result, replacements)


def symbolically_execute_path(file_path, address, se_context, path):
    """
    :param file_path: string
    :param address: int
    :param se_context: SEContext
    :param path: list of LocKeys

    :returns: OutputResultEntry
    """
    container = Container.from_stream(open(file_path, "rb"))
    machine = Machine(container.arch)
    mdis = machine.dis_engine(container.bin_stream)

    ira = machine.ira(mdis.loc_db)
    asm_cfg = mdis.dis_multiblock(address)
    ir_cfg = ira.new_ircfg_from_asmcfg(asm_cfg)

    se, replacements = gen_se(ira, se_context)

    result = _symbolically_execute_path(ira, ir_cfg, path, se=se)
    result = SeResultEntry(path, result)

    return filter_output(result, replacements)


def symbolically_execute_all_paths_alt(ira, cfg, address, se_context):
    head = cfg.loc_db.get_offset_location(address)

    se, replacements = gen_se(ira, se_context)

    for entry in _symbolically_execute_all_paths(ira, cfg, head, se=se):
        output_res_entry = filter_output(entry, replacements)
        if se.output_instr_offset:
            output_res_entry = OutputResultEntry(output_res_entry.path,
                                                 output_res_entry.output,
                                                 se.output_instr_offset)
        yield output_res_entry


def symbolically_execute_all_paths(file_path, address, se_context):
    """
    Generator function

    :param file_path: string
    :param address: int
    :param se_context: SEContext

    :returns: yields instances of OutputResultEntry
    """
    container = Container.from_stream(open(file_path, "rb"))
    machine = Machine(container.arch)
    mdis = machine.dis_engine(container.bin_stream)

    ira = machine.ira(mdis.loc_db)
    asm_cfg = mdis.dis_multiblock(address)
    ir_cfg = ira.new_ircfg_from_asmcfg(asm_cfg)

    head = asm_cfg.loc_db.get_offset_location(address)

    se, replacements = gen_se(ira, se_context)

    for entry in _symbolically_execute_all_paths(ira, ir_cfg, head, se=se):
        output_res_entry = filter_output(entry, replacements)
        if se.output_instr_offset:
            output_res_entry = OutputResultEntry(output_res_entry.path,
                                                 output_res_entry.output,
                                                 se.output_instr_offset)
        yield output_res_entry


def replace_expressions(dct, replacements):
    _dct = {}

    for dst, src in dct.items():
        _dst = dst.replace_expr(replacements)
        _src = src.replace_expr(replacements)
        _dct[_dst] = _src

    return _dct


def filter_outputs(se_result_entries, replacements):
    _output_result_entries = []

    for entry in se_result_entries:
        _output_result_entry = filter_output(entry, replacements)
        if not _output_result_entry is None:
            _output_result_entries.append(_output_result_entry)

    return _output_result_entries


def filter_output(entry, replacements):
    assert isinstance(entry, SeResultEntry)

    _state = replace_expressions(entry.state, replacements)
    if OUTPUT in _state.keys():
        _output = _state[OUTPUT]
        _output = _output.replace_expr(replacements)
        return OutputResultEntry(entry.path, _output, None)

    return None


class IOSE(SymbolicExecutionEngine):
    def __init__(self, ira, input_x, input_y, output):
        super(IOSE, self).__init__(ira)
        self.input_x = input_x
        self.input_y = input_y
        self.output = output

        self.output_instr_offset = None
        self.input_x_instr_offset = None
        self.input_y_instr_offset = None
        self.current_instr_offset = None

    def eval_updt_assignblk(self, assignblk):
        self.current_instr_offset = assignblk.instr.offset
        super(IOSE, self).eval_updt_assignblk(assignblk)

    def apply_change(self, dst, src):
        self.check_if_io(dst, src)
        super(IOSE, self).apply_change(dst, src)


    def check_if_io(self, dst, src):
        if self.output in dst and not self.output_instr_offset:
            self.output_instr_offset = self.current_instr_offset
        elif self.input_x in src and not self.input_x_instr_offset:
            self.input_x_instr_offset = self.current_instr_offset
        elif self.input_y in src and not self.input_y_instr_offset:
            self.input_y_instr_offset = self.current_instr_offset


def gen_se(ira, se_context):
    replacements = gen_replacements(se_context.context_addr, se_context.bytecode_addr)
    input_x, input_y, output = get_ios(replacements)
    replacements = assign_values(replacements, se_context)

    # se = SymbolicExecutionEngine(ira)
    se = IOSE(ira, input_x, input_y, output)

    for dst, src in replacements.items():
        se.symbols[dst] = src

    return se, replacements


def get_ios(dct):
    _input_x = X
    _input_y = Y
    _output = None

    for k, v in dct.items():
        if v == OUTPUT:
            _output = k

    assert _input_x and _input_y and _output

    return _input_x, _input_y, _output


def assign_values(replacements, se_context):
    assignments = {}
    if not se_context.x_val is None:
        assignments[X] = ExprInt(se_context.x_val, X.size)
    if not se_context.y_val is None:
        assignments[Y] = ExprInt(se_context.y_val, Y.size)
    if not se_context.c_val is None:
        assignments[C] = ExprInt(se_context.c_val, C.size)
    if not se_context.key_val is None:
        assignments[KEY] = ExprInt(se_context.key_val, KEY.size)

    _replacements = {}
    for dst, src in replacements.items():
        _replacements[dst] = src.replace_expr(assignments)

    return _replacements


def _symbolically_execute_path(ira, cfg, path, se=None):
    """
    Symbolically executes a specific path.
    """

    assert is_path_in_cfg(cfg, path)

    if se is None:
        se = SymbolicExecutionEngine(ira)

    for loc in path:
        se.run_block_at(cfg, loc)

    return dict(se.state)


def _symbolically_execute_all_paths(ira, cfg, start_loc, se=None):
    """
    Symbolically executes all combinatorically possible paths. However, if  IRDsts
    evaluate to a specific LocKey, the other jump location is not taken for that
    specific path, which somewhat reduces the set of paths.
    """
    assert isinstance(start_loc, LocKey)

    if se is None:
        se = SymbolicExecutionEngine(ira)

    assert start_loc in cfg.blocks

    _next_loc = se.run_block_at(cfg, start_loc)
    _next_loc = transform_to_loc_key(_next_loc, cfg.loc_db)
    tmp_loc = start_loc

    leaves = cfg.leaves()
    if start_loc in leaves:
        yield SeResultEntry([start_loc], dict(se.state))
        return

    if isinstance(_next_loc, LocKey):
        _succs = [_next_loc]
    else:
        _succs = cfg.successors(start_loc)

    tmp_succs = {start_loc: Checkpoint(se.get_state(),
                                       _succs,
                                       [start_loc])}

    se_result = []

    while True:
        se.set_state(tmp_succs[tmp_loc].state)
        tmp_path = list(tmp_succs[tmp_loc].path)

        try:
            tmp_loc = tmp_succs[tmp_loc].succs.pop()
        except IndexError:
            # All successors of the current block
            # have been processed at this stage.
            del tmp_succs[tmp_loc]

            if tmp_loc == start_loc:
                return

            tmp_loc = tmp_path[-2]
            continue

        _next_loc = se.run_block_at(cfg, tmp_loc)
        _next_loc = transform_to_loc_key(_next_loc, cfg.loc_db)
        tmp_path.append(tmp_loc)

        if tmp_loc in leaves:
            yield SeResultEntry(tmp_path, dict(se.state))
            tmp_loc = tmp_path[-2]
            continue

        if isinstance(_next_loc, LocKey):
            _succs = [_next_loc]
        else:
            _succs = cfg.successors(tmp_loc)

        tmp_succs[tmp_loc] = Checkpoint(se.get_state(),
                                        _succs,
                                        tmp_path)


def symbol_mem_read(address: Expr) -> Expr:
    return expr_simp_explicit(expr_simp(ExprMem(address, 64)))


def gen_replacements(context_address: int, bytecode_address: int) -> Dict[Expr, Expr]:
    # init
    context = ExprInt(context_address, 64)
    bytecode = ExprInt(bytecode_address, 64)
    vip = context + ExprInt(8, 64)  # build addresses
    output_address = (ExprMem(ExprMem(vip, 64) + bytecode + ExprInt(0, 64), 16).zeroExtend(64) * ExprInt(8,
                                                                                                         64)) + context
    x_address = (ExprMem(ExprMem(vip, 64) + bytecode + ExprInt(2, 64), 16).zeroExtend(64) * ExprInt(8, 64)) + context
    y_address = (ExprMem(ExprMem(vip, 64) + bytecode + ExprInt(4, 64), 16).zeroExtend(64) * ExprInt(8, 64)) + context
    c_address = ExprMem(vip, 64) + bytecode + ExprInt(6, 64)
    key_address = ExprMem(vip, 64) + bytecode + ExprInt(14, 64)  # replacements
    return {
        symbol_mem_read(output_address): OUTPUT,
        symbol_mem_read(x_address): X,
        symbol_mem_read(y_address): Y,
        symbol_mem_read(c_address): C,
        symbol_mem_read(key_address): KEY,
    }
