from collections import namedtuple

from miasm.analysis.binary import Container
from miasm.analysis.machine import Machine
from miasm.expression.simplifications import expr_simp_explicit
from miasm.ir.symbexec import SymbolicExecutionEngine, SymbolMngr

from .helper import *

TaintSource = namedtuple("TaintSource", "expr instr_offset")


def taint_analysis_miasm_alt(ira, cfg, path, context_address, bytecode_address):
    taint_sources = gen_taint_sources(context_address, bytecode_address, ira, cfg, path)

    te = TaintEngine(ira, taint_sources, cfg)
    te.analyze_path(path)

    return te.tainted_instructions, te.visited_instructions


def taint_analysis_miasm(file_path, address, path, context_address, bytecode_address):
    container = Container.from_stream(open(file_path, "rb"))
    machine = Machine(container.arch)
    mdis = machine.dis_engine(container.bin_stream)

    ira = machine.ira(mdis.loc_db)
    asm_cfg = mdis.dis_multiblock(address)
    ir_cfg = ira.new_ircfg_from_asmcfg(asm_cfg)

    taint_sources = gen_taint_sources(context_address, bytecode_address, ira, ir_cfg, path)

    te = TaintEngine(ira, taint_sources, ir_cfg)
    te.analyze_path(path)

    return te.tainted_instructions, te.visited_instructions


def gen_taint_sources(context_address, bytecode_address, ira, ir_cfg, path):
    context = ExprInt(context_address, 64)
    bytecode = ExprInt(bytecode_address, 64)
    vip = context + ExprInt(8, 64)  # build addresses

    x_address = (ExprMem(ExprMem(vip, 64) + bytecode + ExprInt(2, 64), 16).zeroExtend(64) * ExprInt(8, 64)) + context
    y_address = (ExprMem(ExprMem(vip, 64) + bytecode + ExprInt(4, 64), 16).zeroExtend(64) * ExprInt(8, 64)) + context
    c_address = ExprMem(vip, 64) + bytecode + ExprInt(6, 64)
    key_address = ExprMem(vip, 64) + bytecode + ExprInt(14, 64)
    x = symbol_mem_read(x_address)
    y = symbol_mem_read(y_address)
    c = symbol_mem_read(c_address)
    key = symbol_mem_read(key_address)
    x = TaintSource(x, None)
    y = TaintSource(y, None)
    c = TaintSource(c, None)
    key = TaintSource(key, None)

    return [x, y, c, key]


def symbol_mem_read(address: Expr) -> Expr:
    return expr_simp_explicit(expr_simp(ExprMem(address, 64)))


class TaintEngine(SymbolicExecutionEngine):
    def __init__(self, arch, taint_sources, ir_cfg, state={}, *arg, **kwargs):
        super(self.__class__, self).__init__(arch, *arg, **kwargs)

        self.init_state = state.copy()

        self.taint_sources = list(taint_sources)
        self.to_be_tainted = {}
        self.tainted_instructions = set()
        self.visited_instructions = set()
        self.tainted_bit_expr_name = "T"
        self.tainted_bit_counter = 0
        self.tainted_bits_created = []
        self.ir_cfg = ir_cfg

    def create_tainted_bit_string(self, length):
        arr = []
        for _ in range(length):
            tainted_bit_name = self.tainted_bit_expr_name+"."+str(self.tainted_bit_counter)
            tainted_bit = ExprId(tainted_bit_name, 1)
            # arr.append(self.tainted_bit_expr)
            arr.append(tainted_bit)
            self.tainted_bits_created.append(tainted_bit)
            self.tainted_bit_counter += 1

        return ExprCompose(*arr)

    def analyze_path(self, path):
        # Resetting the SymbolManager before each analysis
        self.symbols = SymbolMngr(addrsize=self.ir_arch.addrsize,
                                  expr_simp=self.expr_simp)
        self.add_to_state(self.init_state)

        self.to_be_tainted = {}
        self.tainted_instructions = set()
        self.visited_instructions = set()
        self.tainted_bit_counter = 0
        self.tainted_bits_created = []
        self.init_taint_pool(self.taint_sources)

        for loc in path:
            self.run_block_at(self.ir_cfg, loc)

    def add_to_state(self, state):
        for dst, src in state.items():
            self.symbols.write(dst, src)

    def init_taint_pool(self, to_be_tainted):
        for taint_src in to_be_tainted:
            assert isinstance(taint_src.expr, ExprMem) or \
                   isinstance(taint_src.expr, ExprId)

            if taint_src.instr_offset is None:
                self.taint_symbol(taint_src.expr)
            else:
                self.to_be_tainted[taint_src.instr_offset] = taint_src.expr

    def taint_symbol(self, expr):
        t_string = self.create_tainted_bit_string(expr.size)
        self.symbols.write(expr, t_string)

    def is_tainted(self, expr):
        for t_bit in self.tainted_bits_created:
            if t_bit in expr:
                return True

        return False

    def eval_updt_assignblk(self, assignblk):
        instr_offset = assignblk.instr.offset
        self.visited_instructions.add(assignblk.instr)

        if instr_offset in self.to_be_tainted:
            expr = self.to_be_tainted[instr_offset]
            self.taint_symbol(expr)

        is_instr_tainted = False
        mem_dst = []
        dst_src = self.eval_assignblk(assignblk)
        for dst, src in viewitems(dst_src):
            self.apply_change(dst, src)

            if self.is_tainted(src):
                is_instr_tainted |= True

            if dst.is_mem():
                mem_dst.append(dst)

        if is_instr_tainted:
            self.tainted_instructions.add(assignblk.instr)

        return mem_dst
