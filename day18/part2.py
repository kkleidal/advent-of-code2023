import sys
import enum
import tqdm
from collections import defaultdict

instructions = []
with open(sys.argv[1], 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            _, _, full_hex = line.split(' ')
            full_hex = int(full_hex.strip('(#)'), 16)
            steps = full_hex // 16
            direction = full_hex % 16
            direction = {
                0: (0, 1),
                2: (0, -1),
                3: (-1, 0),
                1: (1, 0),
            }[direction]
            instructions.append((direction, steps, None))

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

class Events:
    ENTER_HORIZ = 0
    EXIT_HORIZ_SWITCH = 1
    EXIT_HORIZ_NOSWITCH = 2
    CROSS_VERT = 3

def add_evt(row_to_events, i, j, evt):
    evts = row_to_events[i]
    if j not in evts or evts[j] > evt:
        evts[j] = evt

print("Enumerating instructions")
row_to_events = defaultdict(dict)
for (d, steps, color), hz, ii in zip(tqdm.tqdm(instructions), horizontal, ignore_interior):
    if d[0] == 0:
        # horizontal
        i = pos[0]
        npos = tuple(x + dx * steps for x, dx in zip(pos, d))
        jmin = min(pos[1], npos[1])
        jmax = max(pos[1], npos[1])
        if ii:
            add_evt(row_to_events, i, jmin, Events.ENTER_HORIZ)
            add_evt(row_to_events, i, jmax, Events.EXIT_HORIZ_NOSWITCH)
        else:
            add_evt(row_to_events, i, jmin, Events.ENTER_HORIZ)
            add_evt(row_to_events, i, jmax, Events.EXIT_HORIZ_SWITCH)
        pos = npos
    else:
        # vertical
        add_evt(row_to_events, pos[0], pos[1], Events.CROSS_VERT)
        for _ in range(steps):
            pos = tuple(x + dx for x, dx in zip(pos, d))
            add_evt(row_to_events, pos[0], pos[1], Events.CROSS_VERT)

print("Consolidating rows")
evts_counts = defaultdict(int)
evts_to_sorted = []
for _, evts in tqdm.tqdm(row_to_events.items(), total=len(row_to_events)):
    evts = frozenset(evts.items())
    evts_counts[evts] += 1

print("Executing unique rows")
total = 0
for evts, counts in tqdm.tqdm(evts_counts.items(), total=len(evts_counts)):
    evts = sorted(evts)
    row_total = 0
    inside = False
    j = jmin

    while evts:
        jat, evt = evts.pop(0)
        if evt == Events.CROSS_VERT:
            if inside:
                row_total += (jat - j) + 1
            inside = not inside
            j = jat
        elif evt == Events.ENTER_HORIZ:
            if inside:
                row_total += (jat - j)
            j = jat
        elif evt == Events.EXIT_HORIZ_SWITCH:
            row_total += (jat - j) + 1
            j = jat + 1
            inside = not inside
        elif evt == Events.EXIT_HORIZ_NOSWITCH:
            row_total += (jat - j) + 1
            j = jat + 1
        else:
            assert False
    assert not inside
    total += row_total * counts
print(total)
