"""
Plugin for dumping MBAs
"""

import sys
import time
from pathlib import Path
from random import getrandbits

sys.path.insert(0, "./miasm")
from miasm.analysis.binary import Container
from miasm.analysis.machine import Machine
from miasm.expression.expression import ExprSlice, ExprOp, ExprCond, ExprCompose, ExprInt, ExprId
from miasm.expression.simplifications import expr_simp
from lokiattack.helper import get_bytecode_address, get_context_address, get_key, get_handler_address
from lokiattack.se import symbolically_execute_all_paths_alt, SEContext, symbolically_execute_path_alt


def miasm_mul(x: ExprId, y: ExprId) -> ExprSlice:
    return ExprSlice(ExprOp('*', ExprCond(ExprSlice(x, 63, 64), ExprCompose(x, ExprInt(0xffffffffffffffff, 64)), ExprCompose(x, ExprInt(0x0, 64))), ExprCond(ExprSlice(y, 63, 64), ExprCompose(y, ExprInt(0xffffffffffffffff, 64)), ExprCompose(y, ExprInt(0x0, 64)))), 0, 64)


def miasm_shl(x: ExprId, y: ExprId) -> ExprOp:
    return x << (ExprCompose(ExprSlice(y, 0, 8), ExprInt(0x0, 56)) & ExprInt(0x3f, 64))


def evaluate(expr, replacements):
    simplified = expr.replace_expr(replacements)
    simplified = expr_simp.expr_simp(simplified)
    assert simplified.is_int()
    return int(simplified)


def compare_io_behavior(expr1, expr2):
    global variables
    rand_vals = []
    replacements = {}
    for v in variables:
        rand_val = getrandbits(v.size)
        replacements[v] = ExprInt(rand_val, v.size)
        rand_vals.append(rand_val)
    try:
        return evaluate(expr1, replacements) == evaluate(expr2, replacements)
    except:
        return False


def has_same_io_behavior(expr1, expr2):
    return all([compare_io_behavior(expr1, expr2) for _ in range(30)])


SET_KEY = True
ALL_SEMANTICS = False
TIMEOUT = 60 * 60

x = ExprId("x", 64)
y = ExprId("y", 64)
c = ExprId("c", 64)
variables = [x, y, c]

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

    if has_same_io_behavior(result.output, core_semantics):
         print(result.output)
         exit()

    observed_semantics.add(result.output)

    # check SE timeout
    if time.time() - start_time > TIMEOUT:
        break
