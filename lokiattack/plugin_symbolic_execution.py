"""
Plugin for symbolic execution (depth 3) based on Miasm
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, "./miasm")
from miasm.analysis.binary import Container
from miasm.analysis.machine import Machine
from miasm.expression.expression import ExprSlice, ExprOp, ExprCond, ExprCompose, ExprInt, ExprId
from lokiattack.helper import get_bytecode_address, get_context_address, get_key, get_handler_address
from lokiattack.se import symbolically_execute_all_paths_alt, SEContext, symbolically_execute_path_alt


def miasm_mul(x: ExprId, y: ExprId) -> ExprSlice:
    return ExprSlice(ExprOp('*', ExprCond(ExprSlice(x, 63, 64), ExprCompose(x, ExprInt(0xffffffffffffffff, 64)), ExprCompose(x, ExprInt(0x0, 64))), ExprCond(ExprSlice(y, 63, 64), ExprCompose(y, ExprInt(0xffffffffffffffff, 64)), ExprCompose(y, ExprInt(0x0, 64)))), 0, 64)


def miasm_shl(x: ExprId, y: ExprId) -> ExprOp:
    return x << (ExprCompose(ExprSlice(y, 0, 8), ExprInt(0x0, 56)) & ExprInt(0x3f, 64))


SET_KEY = True
ALL_SEMANTICS = False
TIMEOUT = 60 * 60

x = ExprId("x", 64)
y = ExprId("y", 64)

handler_key_pos = [
    # x + y
    (2, 4, x + y),
    # x - y
    (3, 8, x - y),
    # x ^ y
    (4, 12, x ^ y),
    # x | y
    (5, 16, x | y),
    # x & y
    (6, 23, x & y),
    # x * y
    (7, 29, miasm_mul(x, y)),
    # x << y
    (8, 35, miasm_shl(x, y)),
]


if len(sys.argv) < 4:
    print(f"[*] Syntax: {sys.argv[0]} <workdir> <core semantics index> <attacker type (static|dynamic)>")
    exit(0)


workdir = Path(sys.argv[1])
core_semantics_index = int(sys.argv[2])
output = workdir.name
if sys.argv[3] == "static":
    SET_KEY = False
elif sys.argv[3] == "dynamic":
    SET_KEY = True
else:
    raise RuntimeError(f"Unexpected value for static|dynamic attacker: {sys.argv[3]}")

if core_semantics_index > 6:
    print("Semantics index out of range.")
    exit(0)

handler_index, key_index, core_semantics = handler_key_pos[core_semantics_index]
num_paths = 0
successful_simplified_semantics = 0
start_time = time.time()

# parse
file_path = workdir / "obf_exe"
bytecode_path = workdir / "byte_code.bin"
context_addr = get_context_address(file_path.as_posix())
bytecode_addr = get_bytecode_address(file_path.as_posix())
# get handler address
address = get_handler_address(file_path.as_posix(), handler_index)
# get key from bytecode file
key = get_key(bytecode_path, key_index)

if SET_KEY:
    se_context = SEContext(context_addr, bytecode_addr, None, None, None, key)
else:
    se_context = SEContext(context_addr, bytecode_addr, None, None, None, None)

container = Container.from_stream(open(file_path, "rb"))
machine = Machine(container.arch)
mdis = machine.dis_engine(container.bin_stream)

ira = machine.ira(mdis.loc_db)
asm_cfg = mdis.dis_multiblock(address)
ir_cfg = ira.new_ircfg_from_asmcfg(asm_cfg)

observed_semantics = set()

# find key-dependent paths
for result in symbolically_execute_all_paths_alt(ira, ir_cfg, address, se_context):
    num_paths += 1

    observed_semantics.add(result.output)

    # check SE timeout
    if time.time() - start_time > TIMEOUT:
        break


# end time measurement
duration = time.time() - start_time


if ALL_SEMANTICS:
    for s in observed_semantics:
        print(s.output)
    exit()

# check success
for s in observed_semantics:
    if s == core_semantics:
        print(f"{output};simplified;{num_paths};{len(observed_semantics)};{duration};{s}")
        exit()

print(f"{output};not simplified;{num_paths};{len(observed_semantics)};{duration};{None}")
