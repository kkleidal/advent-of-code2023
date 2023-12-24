import sys
import math
from fractions import Fraction
import logging
import numpy as np
import itertools
import tqdm
from functools import partial
import multiprocessing
from contextlib import nullcontext

def to_frac(x):
    return Fraction(int(x), 1)

hailstones = []
with open(sys.argv[1], 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            hailstones.append(tuple(tuple(map(to_frac, part.split(', '))) for part in line.split(' @ ')))

def sgn(x):
    if x > 0:
        return 1
    elif x == 0:
        return 0
    else:
        return -1


def dovetail(start, minn, maxx):
    max_dev = 1
    seen = True
    all_seen = set()
    while seen:
        seen = False
        for d1, d2 in sorted(itertools.chain(
            zip(
                range(max(minn, start-max_dev), min(maxx, start+max_dev)+1),
                itertools.repeat(max_dev),
            ),
            zip(
                range(max(minn, start-max_dev), min(maxx, start+max_dev)+1),
                itertools.repeat(-max_dev),
            ),
            zip(
                itertools.repeat(max_dev),
                range(max(minn, start-max_dev)+1, min(maxx, start+max_dev)),
            ),
            zip(
                itertools.repeat(-max_dev),
                range(max(minn, start-max_dev)+1, min(maxx, start+max_dev)),
            ),
        ), key=lambda x: sum(map(abs,x))):
            if d1 < minn or d1 > maxx or d2 < minn or d2 > maxx:
                continue
            assert (d1, d2) not in all_seen
            yield (d1, d2)
            all_seen.add((d1, d2))
            seen = True
        if not seen:
            break
        max_dev += 1
    

def is_integral(x):
    if isinstance(x, Fraction):
        return x.denominator == 1
    return abs(round(float(x)) - x) < 1e-7


def get_pos(hailstone, t):
    x, v = hailstone
    return tuple(x0 + t * vv for x0, vv in zip(x, v))


def will_collide_at(hailstone, rock):
    t = None
    for d in range(3):
        x1, vx1 = [v[d] for v in hailstone]
        x2, vx2 = [v[d] for v in rock]
        if vx2 == vx1:
            continue
        t = (x1 - x2) / (vx2 - vx1)
    if t is None:
        return None
    if get_pos(hailstone, t) != get_pos(rock, t):
        # Doesn't collide in y or z
        return None
    return t


def permutations():
    yield [0, 1, 2], [0, 1, 2]
    yield [1, 0, 2], np.argsort([1, 0, 2]).tolist()
    yield [1, 2, 0], np.argsort([1, 2, 0]).tolist()
    yield [2, 1, 0], np.argsort([2, 1, 0]).tolist()
    yield [2, 0, 1], np.argsort([2, 0, 1]).tolist()
    yield [0, 2, 1], np.argsort([0, 2, 1]).tolist()


def apply_permutation(x, permutation):
    return [x[i] for i in permutation]


def pairs():
    for i in range(len(hailstones)):
        for j in range(1, len(hailstones)):
            yield (i, j)


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


crossing_pairs = []
for pair in pairs():
    if cross_2d(hailstones[pair[0]], hailstones[pair[1]]):
        crossing_pairs.append(pair)
        if len(crossing_pairs) >= 3:
            break


def find(velos):
    rvx, rvy = velos

    one_passed = False
    for (dim_permutation, reverse_permu), (i, j) in itertools.product(
            list(permutations()),
            crossing_pairs,
    ):
        permute = partial(apply_permutation, permutation=dim_permutation)
        unpermute = partial(apply_permutation, permutation=reverse_permu)
        
        hs1 = tuple(map(permute, hailstones[i]))
        hs2 = tuple(map(permute, hailstones[j]))
        ((x1, y1, z1), (vx1, vy1, vz1)) = hs1
        ((x2, y2, z2), (vx2, vy2, vz2)) = hs2

        c1x1 = rvx - vx1
        c1y1 = rvy - vy1
        c1x2 = rvx - vx2
        c1y2 = rvy - vy2
        if c1x1 == 0 or c1x2 == 0:
            continue
        c21 = c1y1 / c1x1
        c22 = c1y2 / c1x2
        if c22 == c21:
            continue
        rpx = (y2 - y1 + c21 * x1 - c22 * x2) / (c21 - c22)
        rpy = y1 - (x1 - rpx) * c21
        one_passed = True

        t1 = (x1 - rpx) / (rvx - vx1)
        if rvy != vy1:
            t1_2 = (y1 - rpy) / (rvy - vy1)
            assert t1 == t1_2

        t2 = (x2 - rpx) / (rvx - vx2) 
        # Next: compute z positions of collision for the two hailstones at the two different collision times
        # From this we can derive the z velocity, and then the z position at time 0
        # check if the z position is integral
        z_coll_1 = get_pos(hs1, t1)[2]
        z_coll_2 = get_pos(hs2, t2)[2]
        if t1 == t2 and z_coll_1 != z_coll_2:
            p = get_pos(((x2, y2), (vx2, vy2)), t2)
            assert get_pos(((x1, y1), (vx1, vy1)), t1) == p
            continue
        rvz = (z_coll_1 - z_coll_2) / (t1 - t2)
        rpz = z_coll_1 - rvz * t1
        if not is_integral(rpz):
            continue

        thrown = (
            tuple(unpermute((rpx, rpy, rpz))),
            tuple(unpermute((rvx, rvy, rvz))),
        )

        assert get_pos(hailstones[i], t1) == get_pos(thrown, t1)
        assert get_pos(hailstones[j], t2) == get_pos(thrown, t2)

        # Then, for each hailstone, compute the time of collision given the known initial position
        # and velocity and see if they're positive and integral. If the are, that's the solution
        # print(rvx, rvy, rpx, rpy, t1, t2)
        times = [will_collide_at(hailstone, thrown) for hailstone in hailstones]
        if all(time is not None for time in times):
            if any(time < 0 for time in times):
                raise NotImplementedError("Negative time")
                continue

            return thrown
        else:
            break
    assert one_passed
    return None

def main(mp=False):
    s = 600
    search = dovetail(0, -s, s)
    for res in tqdm.tqdm(map(find, search), total=(s*2+1)**2):
        if res is not None:
            thrown = res
            print(thrown)
            print(sum(thrown[0]))
            return thrown


if __name__ == "__main__":
    main()

# 1007148211789625
