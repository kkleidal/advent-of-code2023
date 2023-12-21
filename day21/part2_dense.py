import sys
from functools import cache
from collections import defaultdict
import tqdm

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

def make_rel(pos):
    return (pos[0] % N, pos[1] % M)

def vec_add(x, y):
    return tuple(xx + yy for xx, yy in zip(x, y))

def vec_diff(x, y):
    return tuple(xx - yy for xx, yy in zip(x, y))

def in_frontier(pos, vec, frontier, dense_frontier):
    npos = vec_add(pos, vec)
    nrel = make_rel(npos)
    if nrel not in garden:
        return True
    if npos in frontier or npos in dense_frontier:
        return True
    return False

def not_in_frontier(pos, vec, frontier):
    npos = vec_add(pos, vec)
    nrel = make_rel(npos)
    if nrel not in garden:
        return True
    if npos in frontier:
        return False
    return True

def find(steps):
    dense_inner_red = 0
    dense_frontier_red = set()
    frontier_red = {start}
    dense_inner_black = 0
    dense_frontier_black = set()
    frontier_black = {start}
    for t in tqdm.trange(steps):
        even = t % 2 == 0
        frontier = frontier_red if even else frontier_black
        dense_frontier = dense_frontier_black if even else dense_frontier_red

        new_pos = set()
        for pos in frontier:
            for vec in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                npos = vec_add(pos, vec)
                nrel = make_rel(npos)
                if nrel in garden and npos not in dense_frontier:
                    new_pos.add(npos)
        if even:
            frontier_black = new_pos
        else:
            frontier_red = new_pos

        to_remove = set()
        for pos in frontier_red:
            if all(in_frontier(pos, vec, frontier_black, dense_frontier_black) for vec in [(-1, 0), (1, 0), (0, -1), (0, 1)]):
                to_remove.add(pos)
        frontier_red -= to_remove
        dense_frontier_red |= to_remove

        to_remove = set()
        for pos in frontier_black:
            if all(in_frontier(pos, vec, frontier_red, dense_frontier_red) for vec in [(-1, 0), (1, 0), (0, -1), (0, 1)]):
                to_remove.add(pos)
        frontier_black -= to_remove
        dense_frontier_black |= to_remove

        to_remove = set()
        for pos in dense_frontier_red:
            if all(not_in_frontier(pos, vec, frontier_black) for vec in [(-1, 0), (1, 0), (0, -1), (0, 1)]):
                to_remove.add(pos)
        dense_frontier_red -= to_remove
        dense_inner_red += len(to_remove)

        to_remove = set()
        for pos in dense_frontier_black:
            if all(not_in_frontier(pos, vec, frontier_red) for vec in [(-1, 0), (1, 0), (0, -1), (0, 1)]):
                to_remove.add(pos)
        dense_frontier_black -= to_remove
        dense_inner_black += len(to_remove)
        # print(t)
        # print((frontier_red, (dense_frontier_red), dense_inner_red))
        # print((frontier_black, (dense_frontier_black), dense_inner_black))

        
    if steps % 2 == 0:
        comps = (len(frontier_red), len(dense_frontier_red), dense_inner_red)
    else:
        comps = (len(frontier_black), len(dense_frontier_black), dense_inner_black)
    print(comps)
    return sum(comps)

for steps in [6, 50, 100, 500, 1000, 5000]:
    print(steps, find(steps))
