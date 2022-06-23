"""
Plugin for program synthesis based on Syntia
"""

import sys
import time
from pathlib import Path
from random import getrandbits

sys.path.insert(0, "./miasm")

from miasm.analysis.binary import Container
from miasm.analysis.machine import Machine
from lokiattack.helper import get_bytecode_address, get_context_address, get_key, get_handler_address
from lokiattack.se import symbolically_execute_all_paths_alt, SEContext, symbolically_execute_path_alt
from miasm.expression.expression import ExprInt, ExprId
from miasm.expression.simplifications import expr_simp
from syntia.mcts.mcts import MCTS, State, rpn_to_infix
from syntia.mcts.game import Game, Variable
from syntia.mcts.grammar import Grammar



def gen_variables(number_of_variables, bitsize):
    variables = []
    for var_index in range(number_of_variables):
        v = Variable("V.{}".format(var_index), bitsize)
        variables.append(v)
    return variables


def gen_io_map(expr_orig, variables):
    io_map = {}

    for _ in range(20):
        rand_vals = []
        expr = expr_orig
        replacements = dict()

        for v in variables:
            rand_val = getrandbits(64)
            replacements[v] = ExprInt(rand_val, v.size)
            rand_vals.append(rand_val)

        # replace vars with ints
        simplified = expr.replace_expr(replacements)
        # apply constant propagation
        simplified = expr_simp.expr_simp(simplified)

        assert simplified.is_int()
        io_map[tuple(rand_vals)] = int(simplified)

    return io_map


def synthesise(expr, variables):
    # mcts config
    bitsize = expr.size
    uct_scalar = 1.5
    mcts_iterations = 50000
    playout_depth = 0
    max_time = SYNTHESIS_TIMEOUT

    # io_map
    io_map = gen_io_map(expr, variables)

    variables = gen_variables(len(variables), bitsize)
    grammar = Grammar(variables, constants=["0", "1"])
    game = Game(grammar, variables, bitsize)
    synthesis_inputs = [list(k) for k in io_map]
    def synthesis_oracle(x): return io_map[tuple(x)]

    # init synthesizer
    mc = MCTS(game, synthesis_oracle, synthesis_inputs, uct_scalar)
    mc.verbosity_level = 0
    mc.playout_nesting = playout_depth
    s = State(game, game.bitsize)

    # synthesis
    synthesis_time_start = time.time()
    mc.search(s, mcts_iterations, max_time)
    synthesis_time_end = time.time()
    duration = synthesis_time_end - synthesis_time_start
    success = 1 if mc.final_expression else 0

    expr = None
    if mc.final_expression:
        expr = rpn_to_infix(mc.final_expression)

    return (success, duration, expr)


SET_KEY = True
PATH_TIMEOUT = 60 * 60
SYNTHESIS_TIMEOUT = 120

k = ExprId("key", 64)
x = ExprId("x", 64)
y = ExprId("y", 64)
c = ExprId("c", 64)

if len(sys.argv) < 4:
    print(f"[*] Syntax: {sys.argv[0]} <file path> <handler index> <key>")
    exit(0)


num_paths = 0
successful_simplified_semantics = 0
start_time = time.time()

# parse
workdir = Path(sys.argv[1])
handler_index = int(sys.argv[2], 16)
key = int(sys.argv[3], 16)

file_path = workdir / "obf_exe"
context_addr = get_context_address(file_path.as_posix())
bytecode_addr = get_bytecode_address(file_path.as_posix())
# get handler address
address = get_handler_address(file_path.as_posix(), handler_index)

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
start_time = time.time()

# find key-dependent paths
for result in symbolically_execute_all_paths_alt(ira, ir_cfg, address, se_context):
    num_paths += 1
    observed_semantics.add(result.output)


        # check SE PA
    if time.time() - start_time > PATH_TIMEOUT:
        break

success_total = 0
duration_synthesis = 0.0

for expr in observed_semantics:
    if SET_KEY:
        success, duration_synth_task, expr = synthesise(expr, [x, y, c])
    else:
        success, duration_synth_task, expr = synthesise(expr, [x, y, c, k])

    duration_synthesis += duration_synth_task
    if success:
        success_total += 1

# end time measurement
duration = time.time() - start_time

print(
    f"{file_path.as_posix()};0x{handler_index:x};0x{key:x};{duration};" \
    f"{duration_synthesis};{len(observed_semantics)};{success_total}"
)
