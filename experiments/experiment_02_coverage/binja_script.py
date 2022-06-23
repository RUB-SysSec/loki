#!/usr/bin/env python3

"""
Get number of basic blocks
"""

import logging
from argparse import ArgumentParser
from pathlib import Path
from time import time
from typing import Any, List, Optional

from binaryninja import BinaryViewType, SymbolType



def setup_logging() -> None:
    """Setup log"""
    # Create handlers
    c_handler = logging.StreamHandler()  # pylint: disable=invalid-name
    f_handler = logging.FileHandler(
        "tracer.log", "w+"
    )  # pylint: disable=invalid-name
    c_handler.setLevel(logging.DEBUG)
    f_handler.setLevel(logging.DEBUG)
    log.setLevel(logging.DEBUG)
    c_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    f_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    )
    log.addHandler(c_handler)
    log.addHandler(f_handler)



def bn_load_or_create_db(path: Path) -> BinaryViewType:
    # check if we analyzed the binary before; If so, return cached DB
    cached_db = path.with_suffix(".bndb")
    if cached_db.is_file():
        return BinaryViewType.get_view_of_file(cached_db)
    # else run initial auto-analysis and cache results
    bv = BinaryViewType.get_view_of_file(path)
    bv.create_database(cached_db)
    return bv


def bn_get_function(path: Path, name: str) -> Optional[Any]:
    bv = bn_load_or_create_db(path)
    for fn in bv.functions:
        # ignore thunks
        if fn.symbol.type == SymbolType.ImportedFunctionSymbol:
            continue
        if fn.name == name:
            return fn
    return None

log = logging.getLogger("Binja")

TESTCASES = [
    "aes_encrypt",
    "des_encrypt",
    "md5",
    "rc4",
    "sha1"
]

def main(workdir: Path, allowlist: List[str]) -> None:
    start_time = time()
    log.info(f"Analyzing binaries in {workdir.as_posix()}..")

    binaries = [tc for tc in workdir.glob("*_orig_exe")
                    if len(allowlist) == 0 or \
                        "_".join(tc.name.split("_")[:-2]) in allowlist]

    for binary in binaries:
        print(f"Analyzing {binary}")
        fn = bn_get_function(binary, "target_function")
        assert fn is not None, "Failed to locate 'target_function'"
        print(f"target_function has {len(list(fn.basic_blocks))} basic blocks")
        # for (i, basic_block) in enumerate(fn.basic_blocks):
        #     print(f"i={i}, bb={basic_block}")
    log.info(f"Done in {round(time() - start_time, 2):.2f}s")


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Build ground truth for correctness tests"
    )
    parser.add_argument(
        "path", nargs=1, help="path to evaluation workdirs directory"
    )
    parser.add_argument(
        "--only", dest="allowlist", action="store", nargs="+", default=[],
        help="only run specific tests"
    )
    args = parser.parse_args() # pylint: disable=invalid-name

    target_path = Path(args.path[0]).resolve() # pylint: disable = invalid-name
    setup_logging()
    main(target_path, args.allowlist)
