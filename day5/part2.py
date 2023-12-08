import sys
from typing import List

seeds = None
current_mapping = None
ranges = None
mappings = {}


class Range:
    def __init__(self, start: int, length: int):
        self.start = start
        self.length = length

    def __and__(self, other):
        minn = max(self.start, other.start)
        maxx = min(self.start + self.length, other.start + other.length)
        return Range(minn, maxx - minn) if maxx > minn else None

    def sub(self, other):
        intersect = self & other
        if intersect is None:
            return [self], None
        else:
            parts = []
            end_int = intersect.start + intersect.length
            end_self = self.start + self.length
            if intersect.start > self.start:
                parts.append(Range(self.start, intersect.start - self.start))
            if end_int < end_self:
                parts.append(Range(end_int, end_self - end_int))
            return parts, intersect
        


with open(sys.argv[1], "r") as f:
    state = 0
    for line in f:
        line = line.strip()
        if state == 0:
            seeds = list(map(int, line.split(": ")[1].split(" ")))
            state = 1
        elif state == 1:
            state = 2
        elif state == 2:
            current_mapping = tuple(line.split(" ")[0].split("-to-"))
            ranges = []
            state = 3
        elif state == 3:
            if line:
                dest_start, src_start, length = tuple(map(int, line.split(" ")))
                ranges.append((Range(src_start, length), Range(dest_start, length)))
            else:
                mappings[current_mapping] = ranges
                ranges = []
                current_mapping = None
                state = 2
    if current_mapping:
        mappings[current_mapping] = ranges

state_transitions = {k1: k2 for (k1, k2) in mappings.keys()}

def unionify(vals: List[Range]) -> Range:
    # Lazy, with redundancy: but in theory we could implement this to deduplicate overlapping ranges.
    # Good enough to solve it though
    return vals

def get_my_next_values(current_value, ranges):
    current_values = [current_value]
    next_values = []
    for src_range, dest_range in ranges:
        new_values = []
        for cv in current_values:
            remaining, intersection = cv.sub(src_range)
            if intersection:
                intersection.start += (dest_range.start - src_range.start)
                next_values.append(intersection)
            new_values.extend(remaining)
        current_values = new_values
    return unionify(current_values + next_values)

def get_next_values(current_values, ranges):
    next_values = []
    for value_rng in current_values:
        next_values.extend(get_my_next_values(value_rng, ranges))
    return unionify(next_values)

state = 'seed'
values = [Range(seeds[i], seeds[i+1]) for i in range(0, len(seeds), 2)]
while state != 'location':
    next_state = state_transitions[state]
    ranges = mappings[(state, next_state)]
    next_values = get_next_values(values, ranges)
    state = next_state
    values = next_values
print(min(rng.start for rng in values))
