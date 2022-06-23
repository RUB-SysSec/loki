#!/usr/bin/python3
"""
Evaluate the results from the experiment (Print some statistics!)
"""

from collections import namedtuple
from typing import List, Union
import sys


if len(sys.argv) < 2:
    print(f"[*] Syntax: {sys.argv[0]} <file>")
    exit(0)
file_path = sys.argv[1]


# full_time: path explosion counter / die zeit synthese + overhead durch pfadsuche
Line = namedtuple("Line", "path success time")

def avg(l: Union[List[int], List[float]]) -> float:
    return sum(l) / len(l)

def to_percentage(number: float) -> str:
    return f"{round(number * 100.0, 2)}%"


with open(file_path, "r", encoding="utf-8") as f:
    content = [l.strip().split(";") for l in f.readlines() if l]

lines = list(map(lambda l: Line(l[0], l[1], l[2]), content))

total_time = sum(map(lambda nt: float(nt.time), lines))
avg_time = (total_time / len(lines))
num_success = sum(map(lambda nt: str(nt.success) == "solved", lines))
num_failed = sum(map(lambda nt: str(nt.success) == "not solved", lines))

if num_success:
    avg_success_time = sum(map(lambda nt: float(nt.time) if str(nt.success) == "solved" else 0.0, lines)) / num_success
else:
    avg_success_time = "-" # type: ignore
assert num_success + num_failed == len(lines), f"File contained {len(lines)} entries, " \
        f"but found only {num_success} + {num_failed} = {num_success + num_failed} successful/failed instances"

print(f"#handlers: {len(lines)}")
print(f"total time: {total_time}s")
print(f"avg time: {total_time / len(lines)}")
print(f"avg time (success): {avg_success_time}")
print(f"#solved: {num_success}")
print(f"%solved: {to_percentage(num_success / len(lines))}")
