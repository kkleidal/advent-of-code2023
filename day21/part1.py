import sys
import numpy as np
from functools import cache
import scipy.sparse

garden = set()
start = None
with open(sys.argv[1], 'r') as f:
    for i, line in enumerate(f):
        line = line.strip()
        for j, c in enumerate(line):
            if c in 'S.':
                if c == 'S':
                    start = (i, j)
                garden.add((i, j))

pos_to_ind = {pos: i for i, pos in enumerate(sorted(garden))}
adj = np.zeros((len(garden), len(garden)), dtype=np.int64)
for i, j in garden:
    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        ni = i + di
        nj = j + dj
        if (ni, nj) in garden:
            oind = pos_to_ind[(i, j)]
            nind = pos_to_ind[(ni, nj)]
            adj[oind, nind] = 1
            adj[nind, oind] = 1
adj = scipy.sparse.coo_matrix(adj)

start_mat = np.zeros((len(garden), len(garden)), dtype=np.int64)
sind = pos_to_ind[start]
start_mat[sind, sind] = 1
start_mat = scipy.sparse.coo_matrix(start_mat)

@cache
def pow_adj(power):
    assert power > 0
    if power == 1:
        return adj
    else:
        if power % 2 == 0:
            sub = pow_adj(power // 2)
            return (sub @ sub) > 0
        else:
            return (pow_adj(power - 1) @ adj) > 0

print(scipy.sparse.coo_matrix.count_nonzero(start_mat @ pow_adj(64)))
