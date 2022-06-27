#!/usr/bin/python3
"""
Evaluate results of symbolic execution and print some stats
"""

import sys
if len(sys.argv) < 2:
    print(f"[*] Syntax: {sys.argv[0]} <file>")
    exit(0)
file_path = sys.argv[1]



def to_percentage(number: float) -> str:
    return f"{round(number * 100.0, 2)}%"


num_tasks = 0
total_time = 0.0
num_success = 0
num_failure = 0
total_time_success = 0.0
total_different_semantics = 0
total_ir_paths = 0

for line in open(file_path):
    # parse
    line = line.strip()
    args = line.split(";")

    instance = args[0].strip()
    success = args[1]
    num_ir_paths = int(args[2])
    num_observed_different_semantics = int(args[3])
    time = float(args[4])
    core_semantics = args[5]

    num_tasks += 1
    total_ir_paths += num_ir_paths
    total_different_semantics += num_observed_different_semantics
    total_time += time
    if success == "not simplified":
        num_failure += 1
        total_time_success += time
    elif success == "simplified":
        num_success += 1
    else:
        print(f"Field is '{success}' (should be 'success' or 'no success')")
        sys.exit(1)


print(f"number of tasks: {num_tasks}")
print(f"avg #IR paths: {total_ir_paths / num_tasks}")
print(f"avg #observed different semantis: {total_different_semantics / num_tasks}")
print(f"total time: {total_time}")
print(f"avg time: {total_time / num_tasks}")
if num_success:
    print(f"avg time (success): {total_time_success / num_success}")
else:
    print("avg time (success): - (No successful simplification found)")
print(f"#success: {num_success}")
print(f"#failure: {num_failure}")
if num_failure:
    print(f"%simplified: {to_percentage(num_success / num_tasks)}")
else:
    print("%simplified: 100.00%")
