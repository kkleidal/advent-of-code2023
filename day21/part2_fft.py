import sys
from functools import cache
from collections import defaultdict
import numpy as np
import scipy.signal

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
position = np.zeros([N, M], dtype=np.uint64)
position[start] = 1
avail = np.zeros([N, M], dtype=np.uint64)
for pos in garden:
    avail[pos] = 1
adj = np.array([
    [0, 1, 0],
    [1, 0, 1],
    [0, 1, 0],
], dtype=np.uint64)

print(avail)
print(position)
print(adj)
for i in range(1, 6):
    avail = scipy.signal.convolve2d(avail, adj, mode='same', boundary='wrap') * (avail > 0)
    print(i, avail[start])

