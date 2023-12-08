import sys

seeds = None
current_mapping = None
ranges = None
mappings = {}

with open(sys.argv[1], "r") as f:
    state = 0
    for line in f:
        line = line.strip()
        if state == 0:
            seeds = map(int, line.split(": ")[1].split(" "))
            state = 1
        elif state == 1:
            state = 2
        elif state == 2:
            current_mapping = tuple(line.split(" ")[0].split("-to-"))
            ranges = []
            state = 3
        elif state == 3:
            if line:
                ranges.append(tuple(map(int, line.split(" "))))
            else:
                mappings[current_mapping] = ranges
                ranges = []
                current_mapping = None
                state = 2
    if current_mapping:
        mappings[current_mapping] = ranges

state_transitions = {k1: k2 for (k1, k2) in mappings.keys()}

def get_next_value(value, ranges):
    for dest_start, src_start, length in ranges:
        if value >= src_start and value < src_start + length:
            return dest_start + (value - src_start)
    return value

state = 'seed'
values = seeds
while state != 'location':
    next_state = state_transitions[state]
    ranges = mappings[(state, next_state)]
    next_values = [get_next_value(value, ranges) for value in values]
    state = next_state
    values = next_values
print(min(values))
