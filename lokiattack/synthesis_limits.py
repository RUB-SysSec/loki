#!/usr/bin/python2

from __future__ import division
import math
import sys
import random
from syntia.mcts.mcts import *
from syntia.mcts.game import Game, Variable
from syntia.mcts.grammar import Grammar
from syntia.mcts.utils import to_sha1, replace_variables
from syntia.utils.utils import dump_to_json
from syntia.utils.paralleliser import Paralleliser
from functools import partial
from multiprocessing import Manager, Pool

BITSIZE = 64

def gen_inputs(num_of_inputs, num_of_samples):
    inputs = []
    for _ in range(num_of_samples):
        current_inputs = []
        for _ in range(num_of_inputs):
            r = create_random_testcase() % BITSIZE
            current_inputs.append(r)
        inputs.append(current_inputs)
    return inputs

def create_random_testcase() -> int:
    choice: int = random.getrandbits(64) % 5
    if choice == 0:
        return random.getrandbits(8)
    if choice == 1:
        return random.getrandbits(16)
    if choice == 2:
        return random.getrandbits(32)
    if choice == 3:
        return random.getrandbits(64)
    if choice == 4:
        special_testcases = [0x0, 0x1, 0x2, 0x80, 0xff, 0x8000, 0xffff, 0x8000_0000, 0xffff_ffff, 0x8000_0000_0000_0000, 0xffff_ffff_ffff_ffff]
        return random.choice(special_testcases)
    raise Exception(f"Unexpected case: choice is {choice} but should be 0 to 4 (included)")

class Parameters:
    def __init__(self, sa_const, samples, iterations, depths):
        self.sa_const = sa_const
        self.samples = samples
        self.iterations = iterations
        self.playout_depths = depths

    def dump_state(self):
        state = OrderedDict()
        state["SA-UCT"] = self.sa_const
        state["number_of_IO_samples"] = self.samples
        state["MCTS_iterations"] = self.iterations
        state["playout_depth"] = self.playout_depths

        return state

    def dump(self):
        sa_const = self.sa_const
        samples = self.samples
        iterations = self.iterations
        playout_depth = self.playout_depths

        return (sa_const, samples, iterations, playout_depth)

class Synthesiser:
    def __init__(self, number_of_variables, expression_depth, number_of_expressions, num_of_samples):
        self.bitsize = BITSIZE
        self.number_of_expressions = number_of_expressions

        self.variables = self.gen_variables(number_of_variables)
        self.variables_grammar = OrderedSet([v.name for v in self.variables])
        
        self.num_of_samples = num_of_samples
        self.inputs = gen_inputs(len(self.variables), self.num_of_samples)
        self.expressions = self.gen_expressions(expression_depth, self.variables)

        self.in_out_map = self.gen_in_out_map()

    def gen_grammar(self, variables, bitsize):
        return Grammar(variables, bitsize=bitsize, constants=["0", "1"])


    def derive_random_layer(self, n, game):
        expr = ""
        while not expr:
            state = State(game, game.bitsize)
            current_layer = 0
            while current_layer < n - 1:
                state = state.next_state()
                if state.is_terminal():
                    break

                current_layer += 1
            if state.is_terminal():
                continue
            state = state.next_state()
            if state.is_terminal() and current_layer == n - 1:
                expr = state.expr

        return expr

    def gen_variables(self, number_of_variables):
        variables = []
        for var_index in range(number_of_variables):
            v = Variable("V.{}".format(var_index), choice([8, 16, 32, 64]) if number_of_variables > 3 else self.bitsize)
            variables.append(v)
        return variables

    def gen_expressions(self, depth, variables):
        expressions = []
        expressions_set = set()
        not_found_counter = 0
        while len(expressions) < self.number_of_expressions:
            bitsize = choice([v.size for v in variables])
            game = Game(self.gen_grammar(variables, bitsize), variables, bitsize=bitsize)
            expr = self.derive_random_layer(depth, game)

            if self.expr_is_invalid(expr, game):
                continue

            if expr in expressions_set and not_found_counter < 1000:
                not_found_counter += 1
                continue

            expressions_set.add(expr)
            expressions.append((expr, game))

        return expressions

    def expr_is_invalid(self, expr, game):
        if "0" in expr.split(" "):
            return True

        inputs = gen_inputs(len(self.variables), self.num_of_samples)
        outputs = []
        for args in inputs:
            expr_new = replace_variables(expr, game.variables.keys(), args)
            output = game.evaluate_expr(expr_new)
            outputs.append(output)

        outputs = set(outputs)
        if len(outputs) == 1 and (0 in outputs or 1 in outputs):
            return True

        return False

    def gen_in_out_map(self):
        in_out_map = dict()
        for index in range(len(self.inputs)):

            for expr, game in self.expressions:
                if expr not in in_out_map:
                    in_out_map[expr] = dict()
                expr_new = replace_variables(expr, self.variables_grammar, self.inputs[index][:len(self.variables)])
                current_inputs_sha1 = to_sha1(str(self.inputs[index]).replace("L", ""))
                in_out_map[expr][current_inputs_sha1] = game.evaluate_expr(expr_new)

        return in_out_map

    def oracle(self, expr, args):
        """
        Synthesis oracle
        :param args: list of inputs
        :return: output
        """
        # calc hash
        args_sha1 = to_sha1(str(args).replace("L", ""))

        # return output
        return self.in_out_map[expr][args_sha1]


def synthesise(commands, result, index):
    command = commands[index]

    number_of_variables = command[0]
    expression_depth = command[1]
    parameters = command[2]

    synthesiser = Synthesiser(number_of_variables, expression_depth, 1, parameters.samples)
    assert(len(synthesiser.expressions) == 1)
    
    expr, game = synthesiser.expressions[0]

    synthesis_oracle = lambda x: synthesiser.oracle(expr, x)

    synthesis_inputs = list(synthesiser.inputs)
    assert(len(synthesis_inputs) == parameters.samples)

    mc = MCTS(game, synthesis_oracle, synthesis_inputs, uct_scalar=parameters.sa_const)
    mc.verbosity_level = 0
    s = State(game, game.bitsize)

    mc.playout_nesting = parameters.playout_depths

    synthesis_time_start = time()
    mc.search(s, parameters.iterations, max_time=120)

    synthesis_time_end = time()

    ret = synthesis_time_end - synthesis_time_start

    result[index] = (ret, 1 if mc.final_expression else 0)


def run_experiment(number_of_variables, expression_depth, number_of_expressions, parameters):
    task_groups = []
    workers = []
    commands = []
    number_of_tasks = 0



    for _ in range(number_of_expressions):
        command = [number_of_variables, expression_depth, parameters]
        commands.append(command)
        number_of_tasks += 1

    mgr = Manager()
    results = mgr.list(range(len(commands)))

    with Pool()  as pool:
        func = partial(synthesise, commands, results)
        pool.map(func, range(len(commands)))

    total_time = 0
    counter = 0
    success = 0
    for r in results:
        if r:
            counter += 1
            total_time += r[0]
            if r[1] == 1:
                success += 1


    results_data = OrderedDict()
    results_data["configuration"] = parameters.dump_state()
    results_data["number_of_tasks"] = counter
    results_data["success"] = success
    results_data["non_success"] = counter - success
    results_data["total_time"] = total_time
    results_data["average_time"] = total_time / number_of_expressions

    return results_data
    
# check stdin
if len(sys.argv) < 4:
    print("[*] Syntax: <number of variables> <expression depth> <output file>")
    sys.exit(0)

# variables and expression depth
number_of_variables = int(sys.argv[1])
expression_depth = int(sys.argv[2])

# output file
output_file = sys.argv[3]

# initial configuration
uct_scalar = 1.5
mcts_iterations = 50000
io_samples = 20
playout_depth = 0 
number_of_expressions = 10000

# initialise
data = OrderedDict()
parameters = Parameters(uct_scalar, io_samples, mcts_iterations, playout_depth)

# run
results = run_experiment(number_of_variables, expression_depth, number_of_expressions, parameters)

# parse
data["initial_configuration"] = parameters.dump_state()
data["number_of_expressions"] = number_of_expressions
data["number_of_variables"] = number_of_variables
data["expression_depth"] = expression_depth
data["results"] = results

# store
dump_to_json(output_file, data)
