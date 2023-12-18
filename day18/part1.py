import sys
from collections import defaultdict

instructions = []
with open(sys.argv[1], 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            direction, steps, color = line.split(' ')
            direction = {
                'R': (0, 1),
                'L': (0, -1),
                'U': (-1, 0),
                'D': (1, 0),
            }[direction]
            color = int(color.strip('(#)'), 16)
            steps = int(steps)
            instructions.append((direction, steps, color))


d = instructions[0][0]
for new_d, steps, _ in instructions[1:]:
    assert (new_d[0] == 0) != (d[0] == 0)
    assert (new_d[1] == 0) != (d[1] == 0)
    assert steps > 0
    d = new_d

I = len(instructions)
horizontal = []
ignore_interior = []
for i in range(I):
    d_mid = instructions[i][0]
    d_left = instructions[(i-1)%I][0]
    d_right = instructions[(i+1)%I][0]
    horiz = (d_mid[0] == 0)
    crossing = (horiz and (d_left == d_right))
    horizontal.append(horiz)
    ignore_interior.append(horiz and not crossing)

grid = defaultdict(lambda: False)
grid_horiz = defaultdict(lambda: False)
grid_ignore_interior = defaultdict(lambda: False)
pos = (0, 0)
# grid[pos] = (kkk


for (d, steps, color), hz, ii in zip(instructions, horizontal, ignore_interior):
    grid[pos] = True
    grid_horiz[pos] = grid_horiz[pos] or hz
    grid_ignore_interior[pos] = grid_ignore_interior[pos] or ii
    for _ in range(steps):
        pos = tuple(x + dx for x, dx in zip(pos, d))
        grid[pos] = True
        grid_horiz[pos] = grid_horiz[pos] or hz
        grid_ignore_interior[pos] = grid_ignore_interior[pos] or ii

imin = min(i for i, _ in grid)
imax = max(i for i, _ in grid)
jmin = min(j for _, j in grid)
jmax = max(j for _, j in grid)

total = 0
for i in range(imin, imax+1):
    row_total = 0
    inside = False
    j = jmin

    def dbg(*args):
        ...
        # if i == 2:
        #     print(*args)

    dbg(f"At i={i}")
    while j < jmax + 1:
        dbg(f"At j={j}")
        if grid[(i, j)]:
            if grid_horiz[(i, j)]:
                dbg("Horizontal")
                switch_inside = not grid_ignore_interior[(i, j)]
                while j < jmax + 1 and grid_horiz[(i, j)]:
                    dbg(f"Going over j={j}")
                    row_total += 1
                    j += 1
                if switch_inside:
                    inside = not inside
                    dbg(f"Switched inside to {inside}")
                else:
                    dbg(f"Kept inside as {inside}")
            else:
                inside = not inside
                dbg(f"Not horizontal, switched inside to {inside}")
                row_total += 1
                j += 1
        elif inside:
            dbg(f"Inside")
            row_total += 1
            j += 1
        else:
            dbg(f"Outside")
            j += 1
    # print(row_total)
    total += row_total
print(total)
