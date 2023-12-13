import sys
import copy
import numpy as np

mats = []
mat = []
with open(sys.argv[1], 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            mat.append([1 if c == '#' else 0 for c in line])
        else:
            mats.append(mat)
            mat = []
if mat:
    mats.append(mat)
mats = [np.array(mat) for mat in mats]

def count_refl_rows(mat):
    count = 0
    for div in range(len(mat) - 1):
        found = True
        delt = 0
        while ((div - delt) >= 0) and (div + 1 + delt) < mat.shape[0]:
            c1 = div - delt
            c2 = div + 1 + delt
            if not np.array_equal(mat[c1], mat[c2]):
                found = False
                break
            delt += 1
        if found:
            count += div + 1
    return count

col_total = 0
row_total = 0
for mat in mats:
    col_total += count_refl_rows(mat.T)
    row_total += count_refl_rows(mat)
print(100 * row_total + col_total)
