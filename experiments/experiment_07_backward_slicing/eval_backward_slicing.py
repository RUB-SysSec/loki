#!/usr/bin/python3
"""
Evaluate the results from experiment 6 backward slicing (Print some statistics!)
"""

import sys
if len(sys.argv) < 2:
    print(f"[*] Syntax: {sys.argv[0]} <file>")
    exit(0)
file_path = sys.argv[1]

num_tasks = 0
num_asm_instructions = 0
total_time = 0.0
num_success = 0
num_failure = 0
total_time_success = 0
total_num_asm_instructions = 0
total_num_sliced_instructions =- 0
total_ir_paths = 0

with open(file_path, "r", encoding="utf-8") as f:
    content = f.readlines()
for line in content:
    # parse
    line = line.strip()
    args = line.split(";")

    instance = args[0].strip()
    num_asm_instructions = int(args[1])
    num_sliced_instructions = int(args[2])
    num_ir_paths = int(args[3])
    time = float(args[4])

    num_tasks += 1
    total_num_asm_instructions += num_asm_instructions
    total_num_sliced_instructions +=  num_sliced_instructions
    total_ir_paths += num_ir_paths
    total_time += time

avg_sliced = 100 * ((total_num_sliced_instructions / num_tasks) / (total_num_asm_instructions / num_tasks))

print(f"number of tasks: {num_tasks}")
print(f"total time: {total_time}")
print(f"avg time: {total_time / num_tasks}")
print(f"avg #IR paths: {total_ir_paths / num_tasks}")
print(f"avg #visited instructions: {total_num_asm_instructions / num_tasks}")
print(f"avg #sliced instructions: {total_num_sliced_instructions / num_tasks}")
print(f"avg %sliced instructions: {avg_sliced}")
