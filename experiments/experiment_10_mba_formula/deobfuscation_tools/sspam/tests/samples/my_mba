# expr = (x ^ 54)

# without identity
# ./engine "x ^ 0x36" -d 1
a = ((54 - x) + ((x * 2) & 146))
b = (a | 178)
c = (a & 178)
d = ((b - c) & 201)
e = ((b - c) | 201)
f = e - d
expr = (((f - 123) + (246 & (((- f) - 1) * 2))) & 255)
