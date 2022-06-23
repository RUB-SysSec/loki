"""
SMT Plugin for LokiAttack; provides CEGAR functionality to find a valid key for our key encodings
"""
import sys
import time
import z3
from pathlib import Path

sys.path.insert(0, "./miasm")
from miasm.analysis.binary import Container
from miasm.analysis.machine import Machine
from miasm.ir.translators.z3_ir import TranslatorZ3
from lokiattack.helper import get_bytecode_address, get_context_address, get_key, get_handler_address
from lokiattack.se import symbolically_execute_all_paths_alt, SEContext, symbolically_execute_path_alt

# 1h timeout in milliseconds
TIMEOUT= 60 * 60 * 1000

if len(sys.argv) < 2:
    print(f"[*] Syntax: {sys.argv[0]} <workdir>")
    exit(0)

workdir = sys.argv[1]
output = workdir.strip("/").split("/")[-1]
translator = TranslatorZ3()
solver = z3.Solver()
equivalence_solver = z3.Solver()

file_path = Path(workdir) / "obf_exe"
bytecode_path = Path(workdir) / "byte_code.bin"
context_addr = get_context_address(file_path.as_posix())
bytecode_addr = get_bytecode_address(file_path.as_posix())
# second hander
address = get_handler_address(file_path.as_posix(), 2)
# third instruction in bytecode file
key = get_key(bytecode_path, 3)

se_context = SEContext(context_addr, bytecode_addr, None, None, None, key)

container = Container.from_stream(open(file_path, "rb"))
machine = Machine(container.arch)
mdis = machine.dis_engine(container.bin_stream)

ira = machine.ira(mdis.loc_db)
asm_cfg = mdis.dis_multiblock(address)
ir_cfg = ira.new_ircfg_from_asmcfg(asm_cfg)

# find key-dependent path
for result in symbolically_execute_all_paths_alt(ira, ir_cfg, address, se_context):
    # symbolically execute without key set
    se_context = SEContext(context_addr, bytecode_addr, None, None, None, None)
    r = symbolically_execute_path_alt(ira, ir_cfg, se_context, result.path)

    # grep symbolic expression
    f = translator.from_expr(r.output)

    # define variables
    x = z3.BitVec("x", 64)
    y = z3.BitVec("y", 64)
    key = z3.BitVec("key", 64)

    # check for addition
    g = x + y

    # add constraints
    solver.add(f == g)
    solver.add(x != z3.BitVecVal(0, 64))
    solver.add(y != z3.BitVecVal(0, 64))
    solver.add(f != z3.BitVecVal(0, 64))
    solver.add((key & z3.BitVecVal(0xffffffff, 64)) != z3.BitVecVal(1, 64))

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
        solving_time += (duration * 1000)

        # check if key has been found
        if checked == z3.sat:
            # parse key value
            val = solver.model()[key].as_long()

            # reset equivalence solver
            equivalence_solver.reset()
            equivalence_solver.set("timeout",TIMEOUT - int(solving_time))

            # add constraints
            equivalence_solver.add(f != g)
            equivalence_solver.add(key == z3.BitVecVal(val, 64))

            # measure solving time
            start_time = time.time()
            equiv_check = equivalence_solver.check()
            duration = time.time() - start_time
            solving_time  += (duration * 1000)

            # if semantically equivalent
            if equiv_check == z3.unsat:
                # exit CEGAR
                success = True
                # symbolically verify that synthesized key triggers  x + y
                # se_context = SEContext(context_addr, bytecode_addr, None, None, None, val)
                # r = symbolically_execute_path_alt(ira, ir_cfg, se_context, result.path)
                # assert(result.output == r.output)
            # add other constraint for next CEGAR iteration
            elif equiv_check == z3.sat:
                val = z3.BitVecVal(equivalence_solver.model()[key].as_long(), 64)
                solver.add(key != val)

        # timeout check
        if solving_time >= TIMEOUT:
            break

    if success:
        print(f"{output};solved;{solving_time / 1000}")
    else:
        print(f"{output};not solved;{solving_time / 1000}")
    break
