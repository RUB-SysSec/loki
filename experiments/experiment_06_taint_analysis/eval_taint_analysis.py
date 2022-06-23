#!/usr/bin/python3
"""
Evaluate the results from experiment 5 taint analysis (Print some statistics!)
"""

import sys
if len(sys.argv) < 2:
    print("[*] Syntax: {} <file>".format(sys.argv[0]))
    exit(0)
file_path = sys.argv[1]

num_tasks = 0
num_asm_instructions = 0
total_time = 0.0
num_success = 0
num_failure = 0
total_time_success = 0
total_num_asm_instructions = 0
total_num_visited_instructions = 0
total_num_tainted_instructions =- 0
total_ir_paths = 0

for line in open(file_path):
    # parse
    line = line.strip()
    args = line.split(";")

    instance = args[0].strip()
    num_asm_instructions = int(args[1])
    num_visited_instructions = int(args[2])
    num_tainted_instructions = int(args[3])
    num_ir_paths = int(args[4])
    time = float(args[5])
    

    num_tasks += 1
    total_num_asm_instructions += num_asm_instructions
    total_num_visited_instructions += num_visited_instructions
    total_num_tainted_instructions +=  num_tainted_instructions
    total_ir_paths += num_ir_paths
    total_time += time


    

print(f"number of tasks: {num_tasks}")
print(f"total time: {total_time}")
print(f"avg time: {total_time / num_tasks}")
print(f"avg #IR paths: {total_ir_paths / num_tasks}")
print(f"avg #disassembled asm instructions: {total_num_asm_instructions / num_tasks}")
print(f"avg #visited instructions: {total_num_visited_instructions / num_tasks}")
print(f"avg #tainted instructions: {total_num_tainted_instructions / num_tasks}")
print(f"avg %tainted instructions: {100 * ((total_num_tainted_instructions / num_tasks) / (total_num_visited_instructions / num_tasks))}")
