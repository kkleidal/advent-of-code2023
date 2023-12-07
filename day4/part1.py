import sys
import re

points = 0
for line in sys.stdin:
    line = line.strip()
    if line:
        winning, mine = [
            {int(num) for num in re.split(r'\s+', part.strip())}
            for part in line.split(": ")[1].split(" | ")
        ]
        points += (1<<len(winning & mine)) >> 1 
print(points)
