#!/usr/bin/python3

"""
Evaluate results from dead code elimination (print some stats)
"""

import sys


if len(sys.argv) < 2:
    print(f"[*] Syntax: {sys.argv[0]} <results file>")
    exit(0)

file_path = sys.argv[1]

targets = set()

num_handlers = 0
total_num_asm_blocks = 0
total_num_asm_instructions_before = 0
total_num_asm_instructions_after = 0
total_num_ir_instructions_before = 0
total_num_ir_instructions_after = 0
total_num_ir_blocks_before = 0
total_num_ir_blocks_after = 0

with open(file_path, "r", encoding="utf-8") as f:
    content = [l.strip() for l in f.readlines() if l.strip()]

for line in content:
    # parse
    line = line.strip()
    args = line.split(";")
    target_name = args[0].strip()
    handler_address = int(args[1], 16)
    num_asm_blocks = int(args[2])
    num_asm_instructions_before = int(args[3])
    num_asm_instructions_after = int(args[4])
    num_ir_instructions_before = int(args[5])
    num_ir_instructions_after = int(args[6])
    num_ir_blocks_before = int(args[7])
    num_ir_blocks_after = int(args[8])

    # sanity checks
    assert num_asm_instructions_before <= num_ir_instructions_before, "More ASM instructions than IR instructions"
    assert num_asm_instructions_before >= num_asm_instructions_after, "More ASM instructions than before DCE"
    assert num_asm_blocks <= num_ir_blocks_before, "More ASM BBs than before DCE"
    assert num_ir_blocks_before >= num_ir_blocks_after, "More IR BBs than before DCE"
    assert num_ir_instructions_before >= num_ir_instructions_after, "More IR instructions than before DCE"

    # update stats
    targets.add(target_name)
    num_handlers += 1
    total_num_asm_blocks += num_asm_blocks
    total_num_asm_instructions_before += num_asm_instructions_before
    total_num_asm_instructions_after += num_asm_instructions_after
    total_num_ir_instructions_before += num_ir_instructions_before
    total_num_ir_instructions_after += num_ir_instructions_after
    total_num_ir_blocks_before += num_ir_blocks_before
    total_num_ir_blocks_after += num_ir_blocks_after


# verify data
assert total_num_asm_instructions_before <= total_num_ir_instructions_before
assert total_num_asm_instructions_before >= total_num_asm_instructions_after
assert total_num_asm_blocks <= total_num_ir_blocks_before
assert total_num_ir_instructions_before >= total_num_ir_instructions_after
assert total_num_ir_blocks_before >= total_num_ir_blocks_after

avg_asm_ins_before = total_num_asm_instructions_before/num_handlers
avg_asm_ins_after  = total_num_asm_instructions_after/num_handlers
asm_ins_dce_percentage = round(100 * (1 - avg_asm_ins_after / avg_asm_ins_before), 2)

avg_ir_ins_before = total_num_ir_instructions_before/num_handlers
avg_ir_ins_after  = total_num_ir_instructions_after/num_handlers
ir_ins_dce_percentage = round(100 * (1 - avg_ir_ins_after / avg_ir_ins_before), 2)


print(f"number of targets: {len(targets)}")
print(f"number of handler/targets: {num_handlers/len(targets)}")
# print(f"average number of assembly blocks/handler: {total_num_asm_blocks/num_handlers}")
print(f"average number of assembly instructions/handler: {total_num_asm_instructions_before/num_handlers}")
print(
    f"average number of assembly instructions/handler (after DCE): {total_num_asm_instructions_after/num_handlers} " \
    f"(-{asm_ins_dce_percentage}%)"
)
print(f"average number of IL instructions/handler: {total_num_ir_instructions_before/num_handlers}")
print(
    f"average number of IL instructions/handler (after DCE): {total_num_ir_instructions_after/num_handlers} " \
    f"(-{ir_ins_dce_percentage}%)"
)
# print(f"average number of IL blocks/handler: {total_num_ir_blocks_before/num_handlers}")
# print(f"average number of IL blocks/handler (after DCE): {total_num_ir_blocks_after/num_handlers}")
