from sspam import simplifier

xor36 = """
cse0Add0 = ((x * 229) + 247)
cse3Add3 = (((cse0Add0 * 237) + 127) + (((cse0Add0 * 38) + 85) & 172))
cse0BitAnd1 = (((-2 * cse3Add3) + 255) & 172)
cse6Add4 = (cse3Add3 + cse0BitAnd1)
cse0BitAnd2 = (((-2 * cse6Add4) + 171) & 228)
cse0BitAnd3 = ((((cse6Add4 + cse0BitAnd2) * 2) + 112) & 228)
cse0Sub2 = (((cse0BitAnd3 - cse0BitAnd2) - cse0BitAnd1) - cse3Add3)
cse4Add8 = (cse0Sub2 + 199)
cse0Mult7 = (-1 * (((cse4Add8 * 2) + 29) & 108))
cse2Add13 = ((-1 * ((((cse4Add8 + cse0Mult7) * 2) + 137) & 146)) + cse0Mult7)
# cse7Add16 = ((cse2Add13 + 55) + (-1 * ((((cse2Add13 + cse0Sub2) * 2) + 168) | 12)))
# result = ((237 * ((((cse7Add16 + (((((-1 * ((((cse7Add16 + cse0Sub2) * 2) + 68) & 158)) + cse0BitAnd3) - cse0BitAnd2) - cse0BitAnd1) - cse3Add3)) * 229) + 12) - 247)) & 255)
"""

print simplifier.simplify(xor36)


# this rule helps a bit :

custom_rules = [("2*(A ^ 127)", "2*(~A)")]

print simplifier.simplify(xor36, custom_rules=custom_rules)

