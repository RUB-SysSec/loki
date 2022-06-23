#!/usr/bin/env python3

"""
Solve key encoding
"""

from pathlib import Path
import time
from z3 import Solver, BitVec, BitVecVal, sat, unsat
from z3 import *
from argparse import ArgumentParser

TIMEOUT= 5 * 60 * 1000


def main(path: Path) -> None:
    # init solver instances
    solver = Solver()
    equivalence_solver = Solver()

    # read formula from stdin
    with open(path, "r", encoding="utf-8") as fd:
        f = eval(fd.read().strip())

    # define variables
    x = BitVec("x", 64)
    y = BitVec("y", 64)
    key = BitVec("k", 64)

    # check for addition
    g = x + y

    # add constraints
    solver.add(f == g)
    solver.add(x != BitVecVal(0, 64))
    solver.add(y != BitVecVal(0, 64))
    solver.add(f != BitVecVal(0, 64))
    solver.add((key & BitVecVal(0xffffffff, 64)) != BitVecVal(1, 64))

    # init CEGAR
    solving_time = 0.0
    success = False

    # CEGAR loop
    while not success:

        # set solver timeout
        solver.set("timeout",TIMEOUT - int(solving_time))

        # measure z3 solving time
        start_time = time.time()
        checked = solver.check()
        duration = time.time() - start_time
        solving_time  += (duration * 1000)

        # check if key has been found
        if checked == sat:
            # parse key value
            val = solver.model()[key].as_long()

            # reset equivalence solver
            equivalence_solver.reset()
            equivalence_solver.set("timeout",TIMEOUT - int(solving_time))

            # add constraints
            equivalence_solver.add(f != g)
            equivalence_solver.add(key == BitVecVal(val, 64))

            # measure solving time
            start_time = time.time()
            equiv_check = equivalence_solver.check()
            duration = time.time() - start_time
            solving_time  += (duration * 1000)

            # if semantically equivalent
            if equiv_check == unsat:
                # exit CEGAR
                success = True
            # add other constraint for next CEGAR iteration
            elif equiv_check == sat:
                val = BitVecVal(equivalence_solver.model()[key].as_long(), 64)
                solver.add(key != val)

        # timeout check
        if solving_time >= TIMEOUT:
            break

    if success:
        print(f"solved;{solving_time/1000}")
    else:
        print(f"not solved;{solving_time/1000}")


if __name__ == "__main__":
    parser = ArgumentParser(description="Run z3 on formula")
    parser.add_argument("formula_file", type=Path, help="z3 formula file")

    main(parser.parse_args().formula_file)
