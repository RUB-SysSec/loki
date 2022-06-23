#!/usr/bin/env python3

"""
Sample a subset of MBAs for faster artifact evaluation
"""

import logging
import random
import re
from argparse import ArgumentParser, Namespace
from pathlib import Path

logger = logging.getLogger("MBA-Sampler")


DATA_DIR = Path("./data").resolve()
DATA_FILE_RE = re.compile(r"(?P<op>[a-z]+)_depth(?P<depth>[0-9]{1,2})\.txt")


def setup_logging(log_level: int = logging.DEBUG) -> None:
    """Setup logger"""
    # Create handlers
    c_handler = logging.StreamHandler()  # pylint: disable=invalid-name
    c_handler.setLevel(log_level)
    logger.setLevel(logging.DEBUG)
    c_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(c_handler)


def sample_file(src_path: Path, dst_path: Path, num_samples: int) -> None:
    with open(src_path, "r", encoding="utf-8") as f:
        mbas = [l.strip() for l in f.readlines() if l.strip()]
    if num_samples > len(mbas):
        logger.error(f"Asked for {num_samples} samples but {src_path.as_posix()} only has {len(mbas)} MBAs")
    assert num_samples <= len(mbas), \
            f"Asked for {num_samples} samples but {src_path.as_posix()} only has {len(mbas)} MBAs"
    subset = random.sample(mbas, k=num_samples)
    with open(dst_path, "w", encoding="utf-8") as f:
        f.write("\n".join(subset) + "\n")


def sample_mbas(target_path: Path, num_samples: int) -> None:
    logger.debug(f"Taking data files from {DATA_DIR.as_posix()}")
    logger.debug(f"Sampling {num_samples} MBAs per file")
    logger.debug(f"Writing sampled files to {target_path.as_posix()}")
    target_path.mkdir()
    for data_file in DATA_DIR.glob("*.txt"):
        m = DATA_FILE_RE.match(data_file.name)
        assert m is not None, f"Data file does not follow expected naming scheme OP_depthDEPTH.txt: {data_file.name}"
        op = m["op"]
        depth = m["depth"]
        logger.debug(f"Processing {data_file.name:<15} -> op={op:<3}, depth={depth:<2}")
        target_file = target_path / data_file.name
        sample_file(data_file, target_file, num_samples)


def main(args: Namespace) -> None:
    if args.path.exists():
        logger.error(f"Targeted directory already exists - {args.path.as_posix()}")
        exit(1)
    sample_mbas(args.path, args.num_samples)


if __name__ == "__main__":
    parser = ArgumentParser(description="Sample a subset of MBA formulas (for Artifact Evaluation)")
    parser.add_argument("num_samples", type=int, help="Number of MBA formulas to sample from")
    parser.add_argument("path", type=Path, help="Directory where to store sampled MBAs (may not exist!)")
    setup_logging()
    main(parser.parse_args())
