import sys
from functools import cache
from collections import defaultdict

garden = set()
start = None
N = 0
M = 0
with open(sys.argv[1], 'r') as f:
    for i, line in enumerate(f):
        line = line.strip()
        if line:
            N += 1
        for j, c in enumerate(line):
            if i == 0:
                M += 1
            if c in 'S.':
                if c == 'S':
                    start = (i, j)
                garden.add((i, j))

one_step_adj = defaultdict(set)
for i, j in garden:
    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        ni = i + di
        nj = j + dj
        if (ni % N, nj % M) in garden:
            one_step_adj[(i, j)].add((ni, nj))

def adj(pos, steps):
    rel_pos = make_rel(pos)
    return {(pos[0] + oi, pos[1] + oj) for oi, oj in rel_adj(rel_pos, steps)}

def make_rel(pos):
    return (pos[0] % N, pos[1] % M)

def vec_add(x, y):
    return tuple(xx + yy for xx, yy in zip(x, y))

def vec_diff(x, y):
    return tuple(xx - yy for xx, yy in zip(x, y))

@cache
def rel_adj(pos, steps):
    if steps == 1:
        return one_step_adj[pos]
    else:
        if steps % 2 == 0:
            sub = rel_adj(pos, steps // 2)
            reachable = set()
            for npos in sub:
                npos_rel = make_rel(npos)
                for rel in rel_adj(npos_rel, steps // 2):
                    reachable.add(vec_add(vec_diff(rel, npos_rel), npos))
            return reachable
        else:
            sub = rel_adj(pos, steps - 1)
            reachable = set()
            for npos in sub:
                npos_rel = make_rel(npos)
                for rel in rel_adj(npos_rel, 1):
                    reachable.add(vec_add(vec_diff(rel, npos_rel), npos))
            return reachable

for steps in [6, 50, 100, 500, 1000, 5000]:
    print(steps, len(adj(start, steps)))
