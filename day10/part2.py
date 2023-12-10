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

def vec_diff(v1, v2):
    return tuple(x - y for x, y in zip(v1, v2))

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
        

assert len(loops) == 2
points_in_loop = loops[0]
stratified_by_row = defaultdict(set)
for i, j in points_in_loop:
    stratified_by_row[i].add(j)

loop = points_in_loop
edge = (vec_diff(loop[-1], loop[-2]), vec_diff(loop[0], loop[-1]))
coord_to_block[start] = edge

def is_vertically_crossing(point):
    if point not in loop:
        return False
    vecs = coord_to_block[point]
    return any(di != 0 for di, _ in vecs)

def is_horizontally_crossing(point):
    if point not in loop:
        return False
    vecs = coord_to_block[point]
    return any(dj != 0 for _, dj in vecs)

def get_horizontal_cross_direction(point):
    i = loop.index(point)
    point_before = loop[(i - 1) % len(loop)]
    point_after = loop[(i + 1) % len(loop)]
    o1 = point_before[0] - point[0]
    o2 = point[0] - point_after[0]
    assert (o1 == 0) != (o2 == 0)
    return o1 if o1 != 0 else o2

total = 0
all_inside = set()
for i, row in sorted(stratified_by_row.items()):
    inside = False
    horizontal_cross = False
    
    for j in range(min(row), max(row)+1):
        if horizontal_cross:
            if is_vertically_crossing((i, j)):
                new_horizontal_cross_direction = get_horizontal_cross_direction((i, j))
                horizontal_cross = False
                if horizontal_cross_direction == new_horizontal_cross_direction:
                    inside = not inside
        else:
            if is_vertically_crossing((i, j)):
                if is_horizontally_crossing((i, j)):
                    horizontal_cross = True
                    horizontal_cross_direction = get_horizontal_cross_direction((i, j))
                else:
                    inside = not inside
        if inside and (i, j) not in loop:
            all_inside.add((i, j))
            total += 1

print(total)
