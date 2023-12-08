import sys
import itertools

state = 0
my_map = {}
for line in sys.stdin:
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
steps = 0
for inst in itertools.cycle(instructions):
    new_positions = []
    for pos in positions:
        pos = my_map[pos][0 if inst == "L" else 1]
        new_positions.append(pos)
    positions = new_positions
    steps += 1
    if all(pos.endswith('Z') for pos in positions):
        break
print(positions)
print(steps)
