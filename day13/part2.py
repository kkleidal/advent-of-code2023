import sys
import copy
import numpy as np
from tqdm import tqdm

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

def get_refl_rows(mat):
    lines = set()
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
            lines.add(div + 1)
    return lines

def find_new_refl_lines(mat):
    orig_cols = get_refl_rows(mat.T)
    orig_rows = get_refl_rows(mat)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            mat[i, j] = 1 - mat[i, j]
            new_cols = get_refl_rows(mat.T) - orig_cols
            new_rows = get_refl_rows(mat) - orig_rows
            if new_cols or new_rows:
                return new_cols, new_rows
            mat[i, j] = 1 - mat[i, j]
    assert False
    

col_total = 0
row_total = 0
for mat in tqdm(mats):
    new_cols, new_rows = find_new_refl_lines(mat)
    col_total += sum(new_cols)
    row_total += sum(new_rows)
print(100 * row_total + col_total)
