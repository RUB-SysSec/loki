from collections import namedtuple

from miasm.analysis.binary import Container
from miasm.analysis.machine import Machine
from miasm.expression.expression import *
from miasm.expression.simplifications import expr_simp, expr_simp_explicit
from miasm.ir.symbexec import SymbolicExecutionEngine, SymbolMngr
from triton import *


class UnsupportedArchitecture(Exception):
    """Raised if architecture not supported by Triton"""


TaintSourceMiasm = namedtuple("TaintSourceMiasm", "register instruction_offset")

MIASM_TRITON_REGISTER_MAP = {}


def taint_analysis_triton_alt(ira, asm_cfg, ir_cfg, arch, bin_stream, path, context_address, bytecode_address):
    taint_sources = gen_taint_sources(context_address, bytecode_address, ira, ir_cfg, path)
    path = make_address_path(path, ir_cfg)

    return forward_taint(asm_cfg, bin_stream, path, taint_sources, arch)


def taint_analysis_triton(file_path, address, path, context_address, bytecode_address):
    container = Container.from_stream(open(file_path, "rb"))
    machine = Machine(container.arch)
    mdis = machine.dis_engine(container.bin_stream)

    ira = machine.ira(mdis.loc_db)
    asm_cfg = mdis.dis_multiblock(address)
    ir_cfg = ira.new_ircfg_from_asmcfg(asm_cfg)

    taint_sources = gen_taint_sources(context_address, bytecode_address, ira, ir_cfg, path)
    path = make_address_path(path, ir_cfg)

    return forward_taint(asm_cfg, container.bin_stream, path, taint_sources, container.arch)


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
    to_be_tainted = set([x, y, c, key])

    se = TaintSourceLocalization(ira)
    taint_sources = se.analyze_path(ir_cfg, path, to_be_tainted)

    return taint_sources


def symbol_mem_read(address: Expr) -> Expr:
    return expr_simp_explicit(expr_simp(ExprMem(address, 64)))


def are_blocks_equivalent(asm_block, ir_block):
    length = len(asm_block.assignblks)
    assert length == len(ir_block.assignblks)

    asm_assignblk_lst = list(asm_block.assignblks)
    ir_assignblk_lst = list(ir_block.assignblks)
    for i in range(length):
        if asm_assignblk_lst[i] != ir_assignblk_lst[i]:
            return False

    return True


def transform_asm_cfg(asm_cfg, bin_stream):
    """
    Returns machine code of asm_cfg:
    {addr: machine code}

    @param asm_cfg: AsmCFG instance. Each block has to have 
    a valid l(ength) attribute and a valid offset attribute.
    
    @param bin_stream: Valid miasm.core.bin_stream instance
    from which asm_cfg was derived.
    """
    code = {}

    for block in asm_cfg.blocks:
        for instr in block.lines:
            byte_cnt = instr.l
            offset = instr.offset
            code[offset] = bin_stream.getbytes(offset, l=byte_cnt)

    return code


def miasm_arch_to_triton_arch(arch_id):
    """
    Maps miasm arch identifier (string) to triton
    arch identifier.
    Architectures supported by triton:
    ARCH.AARCH64 #TODO: look up equivalent arch in miasm.
    ARCH.X86
    ARCH.X86_64
    """

    if arch_id == "x86_32":
        return ARCH.X86
    elif arch_id == "x86_64":
        return ARCH.X86_64
    else:
        raise UnsupportedArchitecture("No equivalent architecture {}" +
                                      " in Triton".format(arch_id))


def make_address_path(path, ir_cfg):
    """
    Transforms elements of path to concrete addresses.
    """
    new_path = []
    for loc_key in path:
        block = ir_cfg.blocks[loc_key]
        for assignblk in block.assignblks:
            new_path.append(assignblk.instr.offset)

    return new_path


def transform_taint_sources(taint_sources):
    """
    Transforms taint_sources [TaintSourceMiasm, ...] to
    {addr, triton_reg}

    @param taint_sources: Array of TaintSourceMiasm instances
    """
    new_taint_sources = {}
    for tsrc in taint_sources:
        reg = MIASM_TRITON_REGISTER_MAP[tsrc.register]
        new_taint_sources[tsrc.instruction_offset] = reg

    return new_taint_sources


def init_register_map(ctx):
    global MIASM_TRITON_REGISTER_MAP

    triton_reg_names = [reg for reg in dir(ctx.registers) if not reg.startswith("__")]

    for reg_name in triton_reg_names:
        reg_obj = getattr(ctx.registers, reg_name)
        bit_size = reg_obj.getBitSize()
        miasm_expr = ExprId(reg_name.upper(), bit_size)
        MIASM_TRITON_REGISTER_MAP[miasm_expr] = reg_obj
        """
        Both, in lower and upper case, because MIASM flag registers are lower case.
        TODO: Needs a fixed constant map for lookup.
        """
        miasm_expr = ExprId(reg_name, bit_size)
        MIASM_TRITON_REGISTER_MAP[miasm_expr] = reg_obj


def forward_taint(asm_cfg, bin_stream, path, taint_sources, arch_id):
    """
    @param asm_cfg: AsmCFG instance. Each block has to have 
    a valid l(ength) attribute and a valid offset attribute.
    
    @param bin_stream: Valid miasm.core.bin_stream instance
    from which asm_cfg was derived.

    @param path: List of specific addresses

    @param taint_sources: (register, instruction_NO) with
    instruction_NO being (loc_key of block, index of line).
    """

    code = transform_asm_cfg(asm_cfg, bin_stream)
    arch_id = miasm_arch_to_triton_arch(arch_id)

    ctx = TritonContext()
    ctx.setArchitecture(arch_id)
    ctx.setMode(MODE.ALIGNED_MEMORY, True)
    ctx.setAstRepresentationMode(AST_REPRESENTATION.PYTHON)
    init_register_map(ctx)

    taint_sources = transform_taint_sources(taint_sources)

    tainted_instr_addresses = set()
    for addr in path:
        instr_code = code[addr]

        instr = Instruction()
        instr.setOpcode(instr_code)
        instr.setAddress(addr)
        ctx.processing(instr)

        if addr in taint_sources:
            ctx.taintRegister(taint_sources[addr])
            tainted_instr_addresses.add(addr)

        if instr.isTainted():
            tainted_instr_addresses.add(addr)

    return tainted_instr_addresses, path


class InstructionTypeNotSupportedException(Exception):
    pass


class TaintSourceLocalization(SymbolicExecutionEngine):
    def __init__(self, ira):
        super(TaintSourceLocalization, self).__init__(ira)
        self.to_be_tainted = set()
        self.taint_sources = []
        self.current_instr = None

    def analyze_path(self, ir_cfg, path, to_be_tainted):
        self.symbols = SymbolMngr(addrsize=self.ir_arch.addrsize,
                                  expr_simp=self.expr_simp)
        self.to_be_tainted = set(to_be_tainted)
        self.taint_sources = []

        for loc_key in path:
            self.run_block_at(ir_cfg, loc_key)

        return self.taint_sources

    def eval_updt_assignblk(self, assignblk):
        self.current_instr = assignblk.instr
        super(TaintSourceLocalization, self).eval_updt_assignblk(assignblk)

    def apply_change(self, dst, src):
        """
        Apply @dst = @src on the current state WITHOUT evaluating both side
        @dst: Expr, destination
        @src: Expr, source
        """
        if dst.is_mem():
            self.mem_write(dst, src)
        else:
            self.add_taint_source(dst, src)
            self.symbols.write(dst, src)

    def add_taint_source(self, dst, src):
        if dst.is_id() and self.is_in_to_be_tainted(src) and dst.size >=8 and dst != self.ir_arch.IRDst:
            self.taint_sources.append(TaintSourceMiasm(dst, self.current_instr.offset))

    def is_in_to_be_tainted(self, expr):
        for t_src in self.to_be_tainted:
            derefs = self.generate_derefs(t_src)

            for deref in derefs:
                if deref in expr:
                    return True

        return False

    def generate_derefs(self, expr):
        assert isinstance(expr, ExprMem)
        derefs = []
        size = expr.size
        ptr = expr.ptr

        _size = 8

        while _size <= size:
            _expr = ExprMem(ptr, _size)
            _size *= 2
            derefs.append(_expr)

        return derefs
