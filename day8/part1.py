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
steps = 0
pos = "AAA"
for inst in itertools.cycle(instructions):
    pos = my_map[pos][0 if inst == "L" else 1]
    steps += 1
    if pos == "ZZZ":
        break
assert pos == "ZZZ"
print(steps)
