#!/usr/bin/env python3

"""
Experiment 12 Limits of Program Synthesis
"""
import json
import os
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Dict, Optional

NUM_CPUS: Optional[int] = os.cpu_count()
assert NUM_CPUS is not None, "os.cpu_count() returned None"


def main(path: Path) -> None:
    data: Dict[int, int] = {}
    for file_ in path.glob("*.json"):
        with open(file_, "r", encoding="utf-8") as f:
            content = json.load(f)
        results = content["results"]
        assert results["success"] + results["non_success"] == results["number_of_tasks"]
        assert results["number_of_tasks"] == 10_000
        data[content["expression_depth"]] = results["success"]
    for k in sorted(list(data.keys())):
        v = data[k]
        p = round(100 * v / 10000, 2)
        print(f"{k:2}: {v:5}/10000 ({p:6.2f}%)")


if __name__ == "__main__":
    parser = ArgumentParser(description="Run experiment 09 MBA diversity")
    parser.add_argument("path", type=Path, help="Path to directory containing synthesis limits files")
    main(parser.parse_args().path)
