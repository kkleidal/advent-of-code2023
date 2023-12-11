import sys
from collections import defaultdict
import numpy as np

galaxies_by_row = defaultdict(set)
with open(sys.argv[1], 'r') as f:
    i = 0
    for line in f:
        line = line.strip()
        if line:
            for j, c in enumerate(line):
                if c == '#':
                    galaxies_by_row[i].add(j)
            i += 1

true_row = 0
galaxies_by_col = defaultdict(set)
for i in range(0, max(galaxies_by_row)+1):
    if len(galaxies_by_row[i]) == 0:
        true_row += 1
    for j in galaxies_by_row[i]:
        galaxies_by_col[j].add(true_row)
    true_row += 1
del galaxies_by_row

true_col = 0
galaxies = set()
for j in range(0, max(galaxies_by_col)+1):
    if len(galaxies_by_col[j]) == 0:
        true_col += 1
    for i in galaxies_by_col[j]:
        galaxies.add((i, true_col))
    true_col += 1
del galaxies_by_col

def dist(p1, p2):
    d = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
    return d

galaxies = list(galaxies)
total = 0
pairs = 0
for i in range(len(galaxies)):
    for j in range(i+1, len(galaxies)):
        total += dist(galaxies[i], galaxies[j])
        pairs += 1
print(total, pairs)
