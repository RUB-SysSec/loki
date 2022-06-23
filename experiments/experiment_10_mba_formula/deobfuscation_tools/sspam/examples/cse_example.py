# Example on how to use cse module

from sspam.tools import cse


expr = "(34 | x) + ((34 | x) & y) - 2*(((34 | x) & y))"

print cse.apply_cse(expr)[0]
