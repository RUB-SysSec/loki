#!/usr/bin/env python3

"""
Run dead code eliminiation (DCE)
"""

from pathlib import Path
import sys

sys.path.insert(0, "./miasm")
from miasm.analysis.binary import Container
from miasm.analysis.data_flow import DeadRemoval, merge_blocks, remove_empty_assignblks
from miasm.analysis.machine import Machine
from miasm.expression.simplifications import expr_simp
from miasm.ir.ir import IRCFG


def write_graph(output_file: Path, cfg: IRCFG) -> None:
    open(output_file, "w", encoding="utf-8").write(cfg.dot())


def count_ir_instructions(cfg: IRCFG) -> int:
    return sum((len(b.assignblks) for b in cfg.blocks.values()))


def count_ir_basic_blocks(cfg: IRCFG) -> int:
    return len(cfg.blocks)


def count_asm_instructions(cfg: IRCFG) -> int:
    ret = set()
    for ir_block in cfg.blocks.values():
        for assign_block in ir_block.assignblks:
            if assign_block.instr.offset is not None:
                ret.add(assign_block.instr.offset)
    return len(ret)


# check args
if len(sys.argv) < 3:
    print(f"[!] Syntax: {sys.argv[0]} <file> <addr>")
    sys.exit()

# parse stdin
file_path = Path(sys.argv[1]) / "obf_exe"
start_addr = int(sys.argv[2], 16)

# read binary file
with open(file_path, "rb") as f:
    container = Container.from_stream(f)
# get CPU abstraction
machine = Machine(container.arch)
# disassembly engine
mdis = machine.dis_engine(container.bin_stream, loc_db=container.loc_db)

# init intermediate representation class
ira = machine.ira(mdis.loc_db)

# build cfgs
asm_cfg = mdis.dis_multiblock(start_addr)
ira_cfg = ira.new_ircfg_from_asmcfg(asm_cfg)

# write IRA graph before simplifications
# write_graph("before_simp.dot", ira_cfg)

# count
asm_instructions_before = count_asm_instructions(ira_cfg)
ir_instructions_before = count_ir_instructions(ira_cfg)
ir_basic_blocks_before = count_ir_basic_blocks(ira_cfg)

# set entry point
entry_points = {mdis.loc_db.get_offset_location(start_addr)}

# dead code elimination
deadrm = DeadRemoval(ira)
ira_cfg.simplify(expr_simp)
modified = True

# fixpoint
while modified:
    modified = False
    modified |= deadrm(ira_cfg)
    modified |= remove_empty_assignblks(ira_cfg)
    modified |= merge_blocks(ira_cfg, entry_points)

# write IRA graph after simplifications
# write_graph("after_simp.dot", ira_cfg)

# count
asm_instructions_after = count_asm_instructions(ira_cfg)
ir_instructions_after = count_ir_instructions(ira_cfg)
ir_basic_blocks_after = count_ir_basic_blocks(ira_cfg)

output = f"{file_path.as_posix()};0x{start_addr:x};{len(asm_cfg.blocks)};" \
         f"{asm_instructions_before};{asm_instructions_after};" \
         f"{ir_instructions_before};{ir_instructions_after};" \
         f"{ir_basic_blocks_before};{ir_basic_blocks_after}"

print(output)
# output
# print("before and after dead code elimination:")
# print("number of asm basic blocks: {}".format(len(asm_cfg.blocks)))
# print("number of asm instructions: {} -> {}".format(asm_instructions_before,
#                                                     asm_instructions_after))
# print("number of IR instructions: {} -> {}".format(ir_instructions_before,
#                                                    ir_instructions_after))
# print("number of IR basic blocks: {} -> {}".format(ir_basic_blocks_before,
#                                                    ir_basic_blocks_after))
