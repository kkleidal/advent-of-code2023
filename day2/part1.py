import sys

maximum = {'red': 12, 'green': 13, 'blue': 14}
total = 0
for line in sys.stdin:
    line = line.strip()
    if line:
        part1, part2 = line.split(": ")
        game_id = int(part1.split(" ")[-1])
        revealed_sets = [{combo.split(" ")[1]: int(combo.split(" ")[0]) for combo in revealed.split(", ")} for revealed in part2.split("; ")]
        possible = all(all(maximum.get(color, 0) >= required for color, required in revealed_set.items()) for revealed_set in revealed_sets)
        if possible:
            total += game_id
print(total)
