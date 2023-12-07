import sys
import re
from functools import reduce

with open(sys.argv[1], "r") as f:
    for line in f:
        splits = re.split(r"\s+", line.strip())
        parts = [int(''.join(splits[1:]))]
        if splits[0] == "Time:":
            times = parts
        else:
            assert splits[0] == "Distance:"
            distances = parts

prod = lambda x: reduce(lambda x, y: x * y, x, 1)

print(prod(
    sum(1 for hold in range(total_time) if (total_time - hold) * hold > best_distance)
    for total_time, best_distance in zip(times, distances)
))
