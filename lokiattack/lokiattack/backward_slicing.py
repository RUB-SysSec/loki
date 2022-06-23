from miasm.analysis.binary import Container
from miasm.analysis.machine import Machine
from miasm.ir.ir import IRCFG, IRBlock, AssignBlock
from miasm.analysis.ssa import *
from miasm.expression.expression import get_expr_mem, ExprMem

from future.utils import viewitems
from collections import namedtuple


MemAssignment = namedtuple("MemAssignment", "expr cfg_loc")


def slice_backwards_path(file_path, address, output_instr_va, path):
    """
    :param file_path: string
    :param address: int
    :param output_instr_va: int, VA of instruction which writes to output
    :param path: list of LocKeys
    :return:
    """
    container = Container.from_stream(open(file_path, "rb"))
    machine = Machine(container.arch)
    mdis = machine.dis_engine(container.bin_stream)

    ira = machine.ira(mdis.loc_db)
    asm_cfg = mdis.dis_multiblock(address)
    ir_cfg = ira.new_ircfg_from_asmcfg(asm_cfg)

    output_instr_loc = va_to_cfg_loc(ir_cfg, output_instr_va)
    sliced_instr_locs = _slice_backwards_path(ir_cfg, path, output_instr_loc)

    return cfg_locs_to_vas(ir_cfg, sliced_instr_locs)


def slice_backwards_path_alt(ir_cfg, output_instr_va, path):
    output_instr_loc = va_to_cfg_loc(ir_cfg, output_instr_va)
    sliced_instr_locs = _slice_backwards_path(ir_cfg, path, output_instr_loc)

    return cfg_locs_to_vas(ir_cfg, sliced_instr_locs)


def _slice_backwards_path(cfg, path, output_instr_loc):
    _cfg = copy_ircfg(cfg)
    ssa_path = BackwardSlicer(_cfg)
    ssa_path.transform(path)
    ssa_exprs = ssa_path.get_ssa_exprs_at_loc(output_instr_loc)
    sliced_instr_locs = set()
    for ssa_expr in ssa_exprs:
        _sliced_instr_locs = ssa_path.slice_backwards(ssa_expr)
        sliced_instr_locs.update(_sliced_instr_locs)

    return sliced_instr_locs


def copy_ircfg(cfg):
    _ir_blocks = {}
    for _loc_key, _block in cfg.blocks.items():
        _assignblks = []
        for _assignblk in _block.assignblks:
            _instr = _assignblk.instr
            _assigns = {}
            for dst, src in _assignblk.iteritems():
                _assigns[dst] = src
            _new_assignblk = AssignBlock(irs=_assigns, instr=_instr)
            _assignblks.append(_new_assignblk)
        _ir_blocks[_loc_key] = IRBlock(_loc_key, _assignblks)

    _cfg = IRCFG(cfg.IRDst, cfg.loc_db, blocks=_ir_blocks)

    return _cfg


class VADoesNotExistExeception(Exception):
    pass


def cfg_locs_to_vas(cfg, cfg_locs):
    _vas = set()
    while True:
        try:
            _cfg_loc = cfg_locs.pop()
        except KeyError:
            return _vas

        _loc_key = _cfg_loc[0]
        _index = _cfg_loc[1]
        _block = cfg.blocks[_loc_key]
        _assignblk = _block.assignblks[_index]
        _vas.add(_assignblk.instr.offset)


def va_to_cfg_loc(cfg, va):
    for _loc_key, _block in cfg.blocks.items():
        _index = 0
        for assignblk in _block.assignblks:
            if assignblk.instr.offset == va:
                return (_loc_key, _index)
            _index += 1

    raise VADoesNotExistExeception


class RHS:
    def __init__(self, rhs, loc):
        self.rhs = rhs
        self.loc = loc

    def get_rhs(self):
        return self.rhs

    def get_loc(self):
        return self.loc


class BackwardSlicer(SSAPath):
    def __init__(self, ircfg):
        self.mem_assignments = {}
        self.path = None
        self.word_size = ircfg.IRDst.size  # assuming arch word size from IRDst
        super(BackwardSlicer, self).__init__(ircfg)

    def transform(self, path):
        self.mem_assignments = {}
        self.path = path
        super(BackwardSlicer, self).transform(path)

    def slice_backwards(self, expr):
        instruction_locations = set()

        if expr.is_mem():
            ids_lhs = self.get_regs(expr)
            for el in ids_lhs:
                tmp_instruction_locations = self._slice_backwards(el)
                instruction_locations.update(tmp_instruction_locations)

        tmp_instruction_locations = self._slice_backwards(expr)

        instruction_locations.update(tmp_instruction_locations)
        return instruction_locations

    def _slice_backwards(self, expr):
        """
        Reassembles an expression in SSA form into a solely non-SSA expression
        :param expr: expression
        :return: non-SSA expression
        """
        #  worklist
        todo = {expr.copy()}
        instruction_locations = set()
        instruction_locations.add(self.ssa_to_location[expr])

        while todo:
            # current expression
            cur = todo.pop()
            # RHS of current expression
            if isinstance(cur, RHS):
                cur_rhs = cur.get_rhs()
                cur_loc = cur.get_loc()
            else:
                cur_rhs = self.expressions[cur]
                cur_loc = self.ssa_to_location[cur]

            # parse ExprIDs on RHS
            ids_rhs = self.get_regs(cur_rhs)
            mems_rhs = get_expr_mem(cur_rhs)
            elmnts_rhs = set()
            elmnts_rhs.update(mems_rhs)
            elmnts_rhs.update(ids_rhs)

            # add RHS ids to worklist
            for el_rhs in elmnts_rhs:
                if el_rhs.is_mem():
                    self.handle_rhs_expr_mem(cur_loc, el_rhs, instruction_locations, todo)
                elif el_rhs in self.expressions:
                    instruction_locations.add(self.ssa_to_location[el_rhs])
                    todo.add(el_rhs)

        return instruction_locations

    def handle_rhs_expr_mem(self, cur_loc, el_rhs, instruction_locations, todo):
        mem_assignmnts = self.retrieve_closest_mem_assignments(cur_loc, el_rhs)
        for mem_assgnmnt in mem_assignmnts:
            rhs_of_rhs = self.get_rhs_from_cfg(mem_assgnmnt.expr, mem_assgnmnt.cfg_loc)
            instruction_locations.add(mem_assgnmnt.cfg_loc)
            todo.add(RHS(rhs_of_rhs, mem_assgnmnt.cfg_loc))

    def get_rhs_from_cfg(self, lhs, loc):
        assignblk = self.ircfg.blocks[loc[0]][loc[1]]
        for dst, src in viewitems(assignblk):
            if lhs == dst:
                return src

    def retrieve_mem_assignments(self, expr_mem):
        ptr = expr_mem.ptr
        assignments = {}

        _size = 8
        while _size <= self.word_size:
            deref = ExprMem(ptr, _size)
            if deref in self.mem_assignments:
                for loc in self.mem_assignments[deref]:
                    assignments[loc] = deref
            _size *= 2

        return assignments

    def retrieve_closest_mem_assignments(self, cur_cfg_loc, expr_mem):
        expr_mem_cfg_locs = self.retrieve_mem_assignments(expr_mem)
        expr_size = expr_mem.size
        # expr_mem_cfg_locs = self.mem_assignments[expr_mem]
        cur_block = cur_cfg_loc[0]
        cur_index = cur_cfg_loc[1]

        for i, loc_key in enumerate(self.path):
            if cur_block == loc_key:
                _index = i

        path = self.path[:_index+1]
        path.reverse()

        resulting_locs = []
        bits_covered = 0
        for loc_key in path:
            tmp_locs, bits_covered = self._retrieve_closest_mem_assignments(loc_key, expr_mem_cfg_locs,
                                                                            cur_block, cur_index, expr_size,
                                                                            bits_covered)
            resulting_locs.extend(tuple(tmp_locs))
            if bits_covered == expr_size:
                break

        return resulting_locs

    def _retrieve_closest_mem_assignments(self, loc_key, expr_mem_cfg_locs,
                                          cur_block, cur_index, expr_size, bits_covered):
        assignment_locs = []
        if loc_key == cur_block:
            s_index = cur_index
        else:
            s_index = len(self.ircfg.blocks[loc_key].assignblks)-1

        indexes = set()
        for a_loc in expr_mem_cfg_locs.keys():
            if a_loc[0] == loc_key:
                indexes.add(a_loc[1])
        indexes = sorted(indexes)
        indexes.reverse()

        for index in indexes:
            if index >= s_index:
                continue

            ass_expr = expr_mem_cfg_locs[(loc_key, index)]
            ass_size = ass_expr.size

            if ass_size > bits_covered:
                bits_covered = ass_size
                assignment_locs.append(MemAssignment(ass_expr, (loc_key, index)))

            if bits_covered == expr_size:
                break

        return assignment_locs, bits_covered

    def _rename_expressions(self, loc_key):
        """
        Transforms variables and expressions
        of an IRBlock into SSA.

        IR representations of an assembly instruction are evaluated
        in parallel. Thus, RHS and LHS instructions will be performed
        separately.
        :param loc_key: IRBlock loc_key
        """
        # list of IRBlock's SSA expressions
        ssa_expressions_block = []

        # retrieve IRBlock
        irblock = self.get_block(loc_key)
        if irblock is None:
            # Incomplete graph
            return

        # iterate block's IR expressions
        for index, assignblk in enumerate(irblock.assignblks):
            # list of parallel instructions
            instructions = self._parallel_instructions(assignblk)
            # list for transformed RHS expressions
            rhs = deque()

            # transform RHS
            for expr in instructions:
                src = expr.src
                src_ssa = self._transform_expression_rhs(src)
                # save transformed RHS
                rhs.append(src_ssa)

            # transform LHS
            for expr in instructions:
                if expr.dst in self.immutable_ids or expr.dst in self.ssa_variable_to_expr:
                    dst_ssa = expr.dst
                else:
                    dst_ssa = self._transform_expression_lhs(expr.dst)

                # retrieve corresponding RHS expression
                src_ssa = rhs.popleft()

                # rebuild SSA expression
                expr = ExprAssign(dst_ssa, src_ssa)
                self.expressions[dst_ssa] = src_ssa
                self.ssa_to_location[dst_ssa] = (loc_key, index)

                if dst_ssa.is_mem():
                    if dst_ssa in self.mem_assignments:
                        self.mem_assignments[dst_ssa].append((loc_key, index))
                    else:
                        self.mem_assignments[dst_ssa] = [(loc_key, index)]

                # append ssa expression to list
                ssa_expressions_block.append(expr)

        # replace blocks IR expressions with corresponding SSA transformations
        new_irblock = self._convert_block(irblock, ssa_expressions_block)
        self.ircfg.blocks[loc_key] = new_irblock

    def get_ssa_exprs_at_loc(self, instr_loc):
        _ssa_exprs = set()
        for _ssa_expr, _loc in self.ssa_to_location.items():
            if _loc == instr_loc:
                _ssa_exprs.add(_ssa_expr)

        return _ssa_exprs
