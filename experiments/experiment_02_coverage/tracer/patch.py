#!/usr/bin/env python3

from functools import partial
import logging
from multiprocessing import Pool
import re
import shutil
import subprocess
from argparse import ArgumentParser, Namespace
from logging import Logger
from pathlib import Path
from typing import List, Optional, Tuple


LOAD_ADDRESS = 0x400000

REPLACEMENT_BYTES = b"\xbb\x01\x00\x00\x00"


def setup_logger(name: str) -> Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def run_objdump(binary: Path, logger: Logger) -> str:
    cmd = ["objdump", "-d", binary.as_posix()]
    try:
        logger.debug(f"Calling {' '.join(cmd)}")
        p = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, \
                            stderr=subprocess.STDOUT, timeout=10)
        logger.debug("objdump completed")
        stdout = p.stdout.decode()
    except subprocess.CalledProcessError as e:
        logger.error(f"objdump error: {str(e)}")
        stdout = e.stdout.decode()
    return stdout


def parse_objdump_output(output: str, logger: Logger) \
            -> Optional[Tuple[int, bytes]]:
    regex = re.compile(r"\s*([A-Fa-f0-9]+)\:\s([A-Fa-f0-9 ]+)\s+mov\s+\$0x2710,%ebx")
    lines = [l.strip() for l in output.splitlines()]
    # TODO: hacky way to parse only main function
    main_lines = []
    in_main = False
    for l in lines:
        if "<main>:" in l:
            in_main = True
        elif l.strip() == "":
            in_main = False
        if in_main:
            main_lines.append(l)
    results: List[Tuple[int, bytes]] = []
    for l in main_lines:
        matches = regex.findall(l)
        if len(matches) == 1:
            addr_str, bytes_str = matches[0]
            addr = int(addr_str, 16)
            bytes_str = bytes_str.strip().replace(" ", "")
            logger.debug(f"bytes_str={bytes_str}")
            expected_bytes = bytes.fromhex(bytes_str)
            results.append((addr, expected_bytes))
    if len(results) != 1:
        logger.error(f"Found {len(results)} but expected 1: {results}")
        return None
    return results[0]


def patch(binary: Path, logger: Logger) -> None:
    """
    Patch a binary
    """
    logger.info(f"Patching {binary.as_posix()}")
    # identify correct address
    # run gdb
    res = parse_objdump_output(
        run_objdump(binary, logger),
        logger
    )
    assert res is not None, f"Failed to locate address for {binary.as_posix()}"
    address, expected_bytes = res
    offset = address - LOAD_ADDRESS
    assert offset > 0, \
            f"Offset must be > 0: {offset:#x} = {address:#} - {LOAD_ADDRESS:#x}"
    assert expected_bytes == b"\xbb\x10\x27\x00\x00", \
            f"Expected bytes 'bb10270000' got '{expected_bytes.hex()}'"
    # prepare patch
    logger.debug(f"offset={offset:#x}, expected_bytes={expected_bytes.hex()}")
    with open(binary, "r+b") as f:
        f.seek(offset)
        before = f.read(5)
        assert before == expected_bytes, "Before patching: " \
                f"Expected {expected_bytes.hex()} got {before.hex()}"
        f.seek(offset)
        f.write(REPLACEMENT_BYTES)
    logger.debug("Patching complete")
    with open(binary, "r+b") as f:
        f.seek(offset)
        after = f.read(5)
        assert after == REPLACEMENT_BYTES, "After patching: " \
                f"Expected {REPLACEMENT_BYTES.hex()} got {after.hex()}"


def copy_binary(src: Path, suffix: str, logger: Logger) -> Path:
    dst = src.parent / (src.name + suffix)
    shutil.copy2(src, dst)
    logger.debug(f"Copying {src.as_posix()} to {dst.name}")
    return dst


def process_binary(logger: Logger, binary: Path) -> None:
    bin_to_patch = copy_binary(binary, "_patched", logger)
    patch(bin_to_patch, logger)


def main(args: Namespace, logger: Logger) -> None:
    path = args.directory
    assert path.exists() and path.is_dir(), f"{path} not found or not a directory"
    instances = path.glob("**/vm_alu*/obf_exe")
    f = partial(process_binary, logger)
    with Pool() as pool:
        pool.map(f, instances)


if __name__ == "__main__":
    parser = ArgumentParser(description="Patch eval binaries to avoid multiple function executions")
    parser.add_argument("directory", type=Path, help="Directory with eval binaries")
    main(parser.parse_args(), setup_logger("Patcher"))
