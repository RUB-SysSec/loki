from sspam import simplifier

xor5c = """
cse0Add0 = ((x * 229) + 247)
cse3Add3 = (((cse0Add0 * 237) + 214) + (((cse0Add0 * 38) + 85) & 254))
cse0Add5 = (((cse3Add3 + (((-1 * (cse3Add3 * 2)) + 255) & 254)) * 3) + 77)
cse0Add7 = ((((((cse0Add5 * 86) + 36) & 70) * 75) + (cse0Add5 * 231)) + 118)
cse0Add9 = (((((cse0Add7 * 58) + 175) & 244) + (cse0Add7 * 99)) + 46)
cse0BitAnd4 = (cse0Add9 & 148)
cse0Add11 = ((((cse0BitAnd4 + (-1 * (cse0Add9 & 255))) + cse0BitAnd4) * 103) + 13)
result = ((237 * ((((cse0Add11 * 45) + (((cse0Add11 * 174) | 34) * 229)) + 194) - 247)) & 255)
"""

print simplifier.simplify(xor5c)
