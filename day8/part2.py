import sys
import itertools
from functools import reduce
import math
import tqdm

state = 0
my_map = {}
with open(sys.argv[1], "r") as f:
    for line in f:
        line = line.strip()
        if state == 0:
            instructions = line
            state = 1
        elif state == 1:
            state = 2
        elif state == 2:
            if line:
                source, neighbors = line.split(" = ")
                left, right = neighbors.strip("()").split(", ")
                my_map[source] = (left, right)

positions = []
for start in my_map:
    if start.endswith("A"):
        positions.append(start)
cycles = []
seen2 = []
for start_pos in positions:
    seen = {(start_pos, 0): 0}
    z_at = set()
    pos = start_pos
    terminates = False
    steps = 0
    for index, inst in itertools.cycle(list(enumerate(instructions))):
        if pos not in my_map:
            terminates = True
            break
        pos = my_map[pos][0 if inst == "L" else 1]
        steps += 1
        state = (pos, (index+1) % len(instructions))
        seen2.append(state)
        if state in seen:
            # cycle
            break
        seen[state] = steps
        if pos.endswith("Z"):
            z_at.add(steps)
    assert not terminates
    assert len(z_at) == 1
    z_time = min(z_at)
    cycle_start = seen[state]
    cycle_len = steps - cycle_start
    assert cycle_len == z_time
    assert seen2[-1] == seen2[-1 - cycle_len]

    a = z_time - cycle_start
    n = cycle_len
    cycles.append((cycle_start, n, z_time))


_, cycle_length, time = cycles[0]

# (time + cycle_length * n) - z_time = 0 mod cycle_len
# (time + cycle_length * n) = z_time mod cycle_len
# cycle_length * n = z_time - time mod cycle_len
for cycle_start, cycle_len, z_time in cycles[1:]:
    cycle_length_mod = cycle_length % cycle_len
    n = 1
    while True:
        n += 1
        if (cycle_length * n) % cycle_len == (z_time - time) % cycle_len:
            break
    time += n * cycle_length
    cycle_length = math.lcm(cycle_length, cycle_len)
    print(time, cycle_length)
print(time)

