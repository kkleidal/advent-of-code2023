import sys
from collections import defaultdict
from functools import reduce

prod = lambda x: reduce(lambda x, y: x * y, x, 1)

maximum = {'red': 12, 'green': 13, 'blue': 14}
total = 0
for line in sys.stdin:
    line = line.strip()
    if line:
        part1, part2 = line.split(": ")
        game_id = int(part1.split(" ")[-1])
        revealed_sets = [{combo.split(" ")[1]: int(combo.split(" ")[0]) for combo in revealed.split(", ")} for revealed in part2.split("; ")]
        minimum_set = defaultdict(int)
        for revealed_set in revealed_sets:
            for color, required in revealed_set.items():
                minimum_set[color] = max(minimum_set[color], required)
        power = prod(minimum_set.values())
        total += power
print(total)
