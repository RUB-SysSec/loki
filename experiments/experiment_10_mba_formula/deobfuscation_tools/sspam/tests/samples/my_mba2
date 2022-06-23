# cse0BitAnd2 = (31 & (((x & 54) - (x | 54)) + 255))

# with identities but without & 255 between affines
# ./engine "x ^ 0x36" -d 1
cse0BitOr0 = (x | 54)
cse0Mult1 = (1 * cse0BitOr0)
cse0BitAnd0 = (x & 54)
cse0BitAnd1 = (31 & (((255 * cse0BitAnd0) + cse0Mult1) + 0))
cse0BitAnd2 = (31 & (((1 * cse0BitAnd0) - cse0Mult1) - 1))
# result = (((229 * ((((((19 * cse0BitAnd1) + (237 * cse0BitAnd2)) + (237 * (62 & (((((2 * cse0BitAnd1) - (2 * cse0BitAnd2)) + (2 * cse0BitAnd0)) - (2 * cse0BitOr0)) - 2)))) - (237 * cse0BitAnd0)) + (237 * cse0BitOr0)) + 144)) + 17) & 255)
