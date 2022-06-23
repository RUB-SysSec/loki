#!/usr/bin/env python3
# pylint: disable = invalid-name
"""
Evaluation results of superhandlers: Determine number of handlers per layer over 1k instances
"""

from argparse import ArgumentParser
from pathlib import Path
from time import time
from typing import Dict, Iterator, List
import logging
import json



logger = logging.getLogger("ComplexityEval")
TIMEOUT = 1800

LAST_LAYER = 20
NUM_INSTANCES = 10



def setup_logging() -> None:
    """Setup logger"""
    c_handler = logging.StreamHandler()  # pylint: disable=invalid-name
    f_handler = logging.FileHandler("complexity.log", "w+")  # pylint: disable=invalid-name
    c_handler.setLevel(logging.DEBUG)
    f_handler.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    c_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    f_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)


def enumerate_files_with_prefix(path: Path, prefix: str) -> Iterator[Path]:
    """Glob all files"""
    for f in (path / "workdirs").glob(prefix + "/instances/*/superhandler_data.txt"):
        yield f


def enumerate_targets() -> Iterator[str]: # Iterator[Path]:
    """Enumerate all possibilities"""
    targets = ["aes", "des", "md5", "rc4", "sha1"]
    types = ["no_superoptimization", "with_superoptimization"]
    for tar in targets:
        for ty in types:
            yield tar + "_" + ty
            #yield enumerate_files_with_prefix(path, tar + ty)


def parse_file(path: Path) -> Iterator[str]:
    """Parse file contents"""
    with open(path, "r", encoding="utf-8") as f:
        content = [l.strip() for l in f.readlines() if l.strip()]
    return map(lambda l: l.split(";")[2], content)


def print_stats(data: Dict[str, List[Dict[int, int]]]) -> None:
    layers_no_superops: Dict[int, int] = {}
    layers_superops: Dict[int, int] = {}
    for k, v in data.items():
        if "with_superoperator" in k:
            assert len(v) == NUM_INSTANCES
            for e in v:
                for layer, cnt in e.items():
                    layers_superops[layer] = layers_superops.get(layer, 0) + cnt
        elif "no_superoperator" in k:
            assert len(v) == NUM_INSTANCES
            for e in v:
                for layer, cnt in e.items():
                    layers_no_superops[layer] = layers_no_superops.get(layer, 0) + cnt
        else:
            RuntimeError(f"Unexpected key: {k}")
    print("Without superoperators (depth : #core semantics):")
    for i in range(1, LAST_LAYER):
        tcnt = float(layers_no_superops.get(i, 0)) / NUM_INSTANCES
        print(f"{i:>2}: {tcnt:>4} " + "#" * round(tcnt))
    print("With superoperators (depth : #core semantics):")
    for i in range(1, LAST_LAYER):
        tcnt = float(layers_superops.get(i, 0)) / NUM_INSTANCES
        print(f"{i:>2}: {tcnt:>4} " + "#" * round(tcnt))

def main(path_no_superopt: Path, path_with_superopt: Path) -> None:
    """Main"""
    start_time = time()
    all_targets: Dict[str, List[Dict[int, int]]] = {}

    for path in (path_no_superopt, path_with_superopt):
        for target in ("aes_encrypt", "des_encrypt", "md5", "rc4", "sha1"):
            prefix = target.replace("_encrypt", "") + "_" + "_".join(path.name.split("_")[-2:])
            all_dicts: List[Dict[int, int]] = []
            for f in list(enumerate_files_with_prefix(path, target)):
                depths_data = list(parse_file(f))
                layer_to_count = {}
                for i in range(1, LAST_LAYER + 1):
                    counts = depths_data.count(str(i))
                    if counts:
                        layer_to_count[i] = counts
                all_dicts.append(layer_to_count)
            assert len(all_dicts) == NUM_INSTANCES, "Failed to parse all files"
            # print(all_dicts)
            all_targets[prefix] = all_dicts
    with open("superhandler_data.txt", "w") as outfile:
        json.dump(all_targets, outfile)
    print_stats(all_targets)
    logger.info(f"Done in {round(time() - start_time, 2)}s")


if __name__ == "__main__":
    parser = ArgumentParser(description="Extract number of core semantics per semantic depth ")
    parser.add_argument("path_no_superopt", type=Path, help="path to evaluation directory *no* superoperators used")
    parser.add_argument("path_with_superopt", type=Path, help="path to evaluation directory *with* superoperators used")
    cargs = parser.parse_args()

    setup_logging()
    main(cargs.path_no_superopt, cargs.path_with_superopt)
