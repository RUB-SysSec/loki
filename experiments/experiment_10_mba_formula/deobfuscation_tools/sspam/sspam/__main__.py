"""
Used to provide a sspam command for the user.
"""


import sys
import argparse

from sspam import simplifier


def main(args=None):
    'The main routine'
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument("expr", type=str, help="expression to simplify")
    parser.add_argument("-n", dest="nbits", type=int,
                        help="number of bits of the variables (default is 8)")
    args = parser.parse_args()
    print(simplifier.simplify(args.expr, args.nbits))


if __name__ == "__main__":
    main()
