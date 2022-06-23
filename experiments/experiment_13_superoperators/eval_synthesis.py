#!/usr/bin/python3
"""
Evaluate the results from experiment 13 synthesis (Print some statistics!)
"""

import sys
from collections import namedtuple
from typing import List, Union

if len(sys.argv) < 2:
    print(f"[*] Syntax: {sys.argv[0]} <file>")
    exit(0)
file_path = sys.argv[1]


# full_time: path explosion counter / die zeit synthese + overhead durch pfadsuche
Line = namedtuple("Line", "path handler_id handler_addr full_time synthesis_time num_tasks num_tasks_synthesized")

def avg(l: Union[List[int], List[float]]) -> float:
    return sum(l) / len(l)

def to_percentage(number: float) -> str:
    return f"{round(number * 100.0, 2)}%"


with open(file_path, "r", encoding="utf-8") as f:
    content = [l.strip().split(";") for l in f.readlines() if l]

lines = list(map(lambda l: Line(l[0], l[1], l[2], l[3], l[4], l[5], l[6]), content))

total_time = sum(map(lambda nt: float(nt.synthesis_time), lines))

synthesis_tasks = sum([int(e.num_tasks) for e in lines])
synthesis_tasks_success = sum([int(e.num_tasks_synthesized) for e in lines])

success_rate = synthesis_tasks_success / synthesis_tasks

print(f"#handlers: {len(lines)}")
print(f"total time: {total_time}")
print(f"avg time: {total_time / len(lines)}")
print(f"#synthesis tasks: {synthesis_tasks}")
print(f"#synthesized synthesis tasks: {synthesis_tasks_success}")
print(f"%successful synthesis tasks: {success_rate} -> {to_percentage(success_rate)}")
