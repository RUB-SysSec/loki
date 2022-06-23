from random import getrandbits

from helper import cast_to_exprint, CastExprComposeExprIntException
from miasm.analysis.binary import Container
from miasm.analysis.machine import Machine
from miasm.expression.expression import *
from miasm.expression.simplifications import expr_simp, expr_simp_explicit
from miasm.ir.symbexec import SymbolicExecutionEngine
from se import _symbolically_execute_path
from syntia.mcts.game import Game, Variable
from syntia.mcts.grammar import Grammar
from syntia.mcts.mcts import *
from syntia.utils.paralleliser import Paralleliser
from z3 import simplify

BITSIZE = 32
IN_OUT_MAP = {}


def synthesis_interface(file_path,
                        address,
                        path,
                        context_addr,
                        bytecode_addr,
                        io_sampling_iterations=30,
                        max_iter=5000,
                        uct_scalar=1.2,
                        num_workers=4):
    container = Container.from_stream(open(file_path, "rb"))
    machine = Machine(container.arch)
    mdis = machine.dis_engine(container.bin_stream)

    ira = machine.ira(mdis.loc_db)
    asm_cfg = mdis.dis_multiblock(address)
    ir_cfg = ira.new_ircfg_from_asmcfg(asm_cfg)

    in_syms = generate_in_syms(context_addr, bytecode_addr)
    out_sym = generate_out_sym(context_addr, bytecode_addr)

    synthesise(ira,
               ir_cfg,
               path,
               in_syms,
               out_sym,
               bitsize=64,
               io_sampling_iterations=io_sampling_iterations,
               max_iter=max_iter,
               uct_scalar=uct_scalar,
               num_workers=num_workers)


def generate_in_syms(context_addr, bytecode_addr):
    context = ExprInt(context_addr, 64)
    bytecode = ExprInt(bytecode_addr, 64)
    vip = context + ExprInt(8, 64)  # build addresses

    x_address = (ExprMem(ExprMem(vip, 64) + bytecode + ExprInt(2, 64), 16).zeroExtend(64) * ExprInt(8, 64)) + context
    y_address = (ExprMem(ExprMem(vip, 64) + bytecode + ExprInt(4, 64), 16).zeroExtend(64) * ExprInt(8, 64)) + context

    return [
        symbol_mem_read(x_address),
        symbol_mem_read(y_address)
    ]


def generate_out_sym(context_addr, bytecode_addr):
    context = ExprInt(context_addr, 64)
    bytecode = ExprInt(bytecode_addr, 64)
    vip = context + ExprInt(8, 64)  # build addresses

    output_address = (ExprMem(ExprMem(vip, 64) + bytecode + ExprInt(0, 64), 16).zeroExtend(64) * ExprInt(8,
                                                                                                         64)) + context

    return symbol_mem_read(output_address)


def symbol_mem_read(address: Expr) -> Expr:
    return expr_simp_explicit(expr_simp(ExprMem(address, 64)))


def oracle(args):
    return IN_OUT_MAP[tuple(args)]


def _synthesis_function(command, result, index):
    ret = ""

    max_iter = command[0]
    uct_scalar = command[1]
    game = command[2]
    oracle = command[3]
    synthesis_inputs = command[4]

    mc = MCTS(game, oracle, synthesis_inputs, uct_scalar=uct_scalar)
    mc.verbosity_level = 2
    s = State(game, BITSIZE)

    mc.search(s, max_iter)

    if mc.final_expression:
        ret = rpn_to_infix(mc.final_expression)
        print("{} ({} iterations)".format(rpn_to_infix(mc.final_expression), mc.current_iter))
        try:
            print("{} (simplified)".format(simplify(game.to_z3(mc.final_expression))))
        except:
            pass

    result[index] = ret


def sample_i_o(ira, ir_cfg, path, in_syms, out_sym, state={}, iterations=30):
    i_o_map = {}

    for _ in range(iterations):
        se = SymbolicExecutionEngine(ira, state=state)

        input_list = []

        for k in in_syms:
            rand = getrandbits(k.size)
            input_list.append(rand)
            se.symbols[k] = ExprInt(rand, k.size)

        _symbolically_execute_path(ir_cfg, path, se=se)

        symbols = dict(se.symbols)
        assert symbols.has_key(out_sym), \
            "{} symbol not contained in SE symbols".format(out_sym)

        try:
            val_out_sym = cast_to_exprint(se.symbols[out_sym])
        except CastExprComposeExprIntException as err:
            print(err)

        assert val_out_sym.is_int(), \
            "{} has no concrete value: {}".format(out_sym, val_out_sym)

        i_o_map[tuple(input_list)] = val_out_sym.arg.arg

    return i_o_map


def synthesise(ira,
               ir_cfg,
               path,
               in_syms,
               out_sym,
               state={},
               bitsize=32,
               io_sampling_iterations=30,
               max_iter=5000,
               uct_scalar=1.2,
               num_workers=4,
               synth_func=_synthesis_function):
    assert check_size(in_syms, bitsize), \
        "Input symbols need to be of specified bitsize ({} bit)\n{}".format(bitsize, in_syms)

    assert out_sym.size == bitsize, \
        "Out symbol {} needs to be of specified bitsize ({} bit)".format(out_sym, bitsize)

    global BITSIZE
    global IN_OUT_MAP
    BITSIZE = bitsize

    i_o_map = sample_i_o(ira, ir_cfg, path, in_syms, out_sym, state=state,
                         iterations=io_sampling_iterations)
    IN_OUT_MAP = i_o_map.copy()

    variables = []
    for var_index in range(len(in_syms)):
        v = Variable("V.{}".format(var_index), bitsize)
        variables.append(v)

    grammar = Grammar(variables)

    game = Game(grammar, variables, bitsize=bitsize)

    task_groups = []
    workers = []
    commands = []

    for index in range(num_workers):
        task_group = "TG"
        task_groups.append(task_group)

        synthesis_inputs = [list(k) for k in i_o_map]
        command = [max_iter, uct_scalar, game, oracle, synthesis_inputs]

        workers.append(synth_func)
        commands.append(command)

    number_of_tasks = len(commands)

    print("Starting main synthesis")
    print(number_of_tasks)

    paralleliser = Paralleliser(commands, workers, number_of_tasks, task_groups)

    start_time = time()
    paralleliser.execute()

    end_time = time()

    print("Synthesis finished in {} seconds".format(end_time - start_time))


def check_size(syms, bitsize):
    for sym in syms:
        assert isinstance(sym, Expr)
        if sym.size != bitsize:
            return False

    return True
