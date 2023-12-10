import sys
import networkx as nx
from collections import defaultdict, Counter

sys.setrecursionlimit(1000000)

def get_block(c):
    if c == '.':
        return None
    elif c == '|':
        return ((-1, 0), (1, 0))
    elif c == '-':
        return ((0, -1), (0, 1))
    elif c == 'L':
        return ((-1, 0), (0, 1))
    elif c == 'J':
        return ((-1, 0), (0, -1))
    elif c == '7':
        return ((1, 0), (0, -1))
    elif c == 'F':
        return ((1, 0), (0, 1))
    elif c == 'S':
        return c
    else:
        assert False, c

rows = []
with open(sys.argv[1], "r") as f:
    for line in f:
        line = line.strip()
        if line:
            rows.append([get_block(c) for c in line])

start = None
coord_to_block = {}
for i, row in enumerate(rows):
    for j, block in enumerate(row):
        if block is not None:
            if block == 'S':
                start = (i, j)
            coord_to_block[(i, j)] = block

def add_vec(pos, vec):
    return tuple(x + y for x, y in zip(pos, vec))

def rev_vec(vec):
    return tuple(-x for x in vec)

neighbor_vecs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

def search_loop(applied_vec, pos, is_start=True, seen=None):
    seen = seen or set()
    seen.add(pos)
    block = coord_to_block[pos]
    assert isinstance(block, tuple)
    counts = Counter(block)
    rv = rev_vec(applied_vec)
    assert counts[rv] >= 1
    counts[rv] -= 1
    next_vec, _ = max(counts.items(), key=lambda x: x[1])
    next_pos = add_vec(pos, next_vec)
    if next_pos not in coord_to_block:
        return None
    if coord_to_block[next_pos] == 'S':
        return [next_pos]
    else:
        if next_pos in seen:
            assert False
        if rev_vec(next_vec) in coord_to_block[next_pos]:
            out = search_loop(next_vec, next_pos, False, seen)
            return [next_pos] + out if out is not None else None
        else:
            return None
    
    
loops = []
for vec in neighbor_vecs:
    next_pos = add_vec(start, vec)
    if next_pos in coord_to_block and rev_vec(vec) in coord_to_block[next_pos]:
        loop = search_loop(vec, next_pos)
        if loop is not None:
            loops.append([next_pos] + loop)
        

def get_longest_path(loop):
    return len(loop) // 2 + (1 if len(loop)%2 != 0 else 0)

print(max(get_longest_path(loop) for loop in loops))

