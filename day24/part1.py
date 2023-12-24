import sys

hailstones = []
with open(sys.argv[1], 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            hailstones.append(tuple(tuple(map(int, part.split(', '))) for part in line.split(' @ ')))

def sgn(x):
    if x > 0:
        return 1
    elif x == 0:
        return 0
    else:
        return -1

def cross_2d(h1, h2):
    x1, v1 = h1
    x2, v2 = h2
    if v1[1] == 0 or v2[1] == 0:
        # Horizontal
        raise NotImplementedError
    m1 = v1[0] / v1[1]
    b1 = x1[0] - x1[1] * m1
    m2 = v2[0] / v2[1]
    b2 = x2[0] - x2[1] * m2
    if m1 == m2:
        return None  # Parallel
    x = (b2 - b1) / (m1 - m2)
    y = m1 * x + b1
    if sgn(x - x1[1]) != sgn(v1[1]):
        return None  # Wrong side of ray
    if sgn(x - x2[1]) != sgn(v2[1]):
        return None  # Wrong side of ray
    return (y, x)

def fmt(hs):
    x, v = hs
    return '%d, %d, %d @ %d, %d, %d' % (*x, *v)


# test_area = (7, 27)
test_area = (200000000000000, 400000000000000)
total = 0
for i in range(len(hailstones)):
    for j in range(i+1, len(hailstones)):
        cross_at = cross_2d(hailstones[i], hailstones[j])
        # print("Hailstone A:", fmt(hailstones[i]))
        # print("Hailstone B:", fmt(hailstones[j]))
        if cross_at:
            if all(x >= test_area[0] and x <= test_area[1] for x in cross_at):
                total += 1
            # print("Cross at", cross_at)
        # print()

print(total)
