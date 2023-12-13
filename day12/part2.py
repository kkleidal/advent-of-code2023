# Dynamic programming
# State is position in row and position in sequence

import sys
from functools import cache

rows = []
with open(sys.argv[1], 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            part1, part2 = line.split(' ')
            seq = list(map(int, part2.split(',')))
            rows.append(('?'.join(5 * [part1]), 5 * seq))

@cache
def count(row, seq, i, j):
    # End cases
    if i == len(row) and j == len(seq):
        return 1
    elif i == len(row):
        return 0
    elif j == len(seq):
        return 1 if all(c in ('.', '?') for c in row[i:]) else 0
        

    # both aren't at end
    total = 0

    # Can we pop from seq?
    next_seq_len = seq[j]
    if (
        i + next_seq_len <= len(row)  # Not past end
        and all(row[ii] == '#' or row[ii] == '?' for ii in range(i, i+next_seq_len))  # All broken or unknown in span
        and (
            (i + next_seq_len == len(row))  # at end
            or row[i+next_seq_len] in ('.', '?')  # next token can be non-broken
        )
    ):
        # print(f'at {i}, use {j}')
        received = count(row, seq, min(i+next_seq_len+1, len(row)), j+1)
        total += received
        # print(f'at {i}, used {j}, received {received}')

    # Can we continue?
    if row[i] in ('?', '.'):
        # print(f'at {i}, try skip {j}')
        received = count(row, seq, i+1, j)
        total += received
        # print(f'at {i}, try skip {j}, received {received}')
    return total

total = 0
for row, seq in rows:
    received = count(tuple(row), tuple(seq), 0, 0)
    print(row, seq, received)
    total += received
print(total)
