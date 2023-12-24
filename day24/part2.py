import sys
import math
from fractions import Fraction
import logging
import numpy as np
import itertools
import tqdm
from functools import partial
import multiprocessing

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

# 
# def fmt(hs):
#     x, v = hs
#     return '%d, %d, %d @ %d, %d, %d' % (*x, *v)


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
    # cross_2d(hailstone, rock)
    (x1, _, _), (vx1, _, _) = hailstone
    (x2, _, _), (vx2, _, _) = rock
    if vx2 == vx1:
        return None
    t = (x1 - x2) / (vx2 - vx1)
    if t < 0:
        return None
    if get_pos(hailstone, t) != get_pos(rock, t):
        # Doesn't collide in y or z
        return None
    return t

# Answer: ((24, 13, 10), (-3, 1, 2))
# test_area = (7, 27)

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

# expected_thrown = ((24, 13, 10), (-3, 1, 2))
# thrown = expected_thrown
# assert will_collide_at(hailstones[-1], thrown) == 1 
# assert will_collide_at(hailstones[-2], thrown) == 6 

def find(velos):
    rvx, rvy = velos
    for (dim_permutation, reverse_permu), (i, j) in itertools.product(
            list(permutations()),
            list(pairs())[:3],
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
            debug("0 slope: not implemented")
            continue
        c21 = c1y1 / c1x1
        c22 = c1y2 / c1x2
        if c22 == c21:
            debug("Parallel: not implemented")
            continue
        rpx = (y2 - y1 + c21 * x1 - c22 * x2) / (c21 - c22) #(y1 - y2 - c21 * x1 + c22 * x2) / (c22 - c21)
        rpy = y1 - (x1 - rpx) * c21

        # if not is_integral(rpx) and not is_integral(rpy):
        #     debug("Non-integral start position")
        #     continue
        
        # c11 = rvx - vx1
        # c12 = rvx - vx2
        # c21 = rvy - vy1
        # c22 = rvy - vy2
        # rpx = ((x1 * c21) / c11 - y1 - (x2 * c22) / c12 + y2) / (c21/c11 - c22/c12)
        # if not is_integral(rpx):
        #     continue
        # rpy = (1 / c11 * rpx - x1 / c11) * c21 + y1

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
            debug(f"Collision in 2 axes, but not in third, {p}, {z_coll_1} vs {z_coll_2}")
            continue
        rvz = (z_coll_1 - z_coll_2) / (t1 - t2)
        rpz = z_coll_1 - rvz * t1
        if not is_integral(rpz):
            debug("Non-integral start position, z")
            continue

        thrown = (
            tuple(unpermute((rpx, rpy, rpz))),
            tuple(unpermute((rvx, rvy, rvz))),
        )

        if t1 < 0 or t2 < 0:
            debug("Negative time")
            continue

        # For debugging:
        # print(expected_thrown)
        # print(thrown)
        # assert expected_thrown == thrown
        # blahh

        assert get_pos(hailstones[i], t1) == get_pos(thrown, t1)
        assert get_pos(hailstones[j], t2) == get_pos(thrown, t2)

        # Then, for each hailstone, compute the time of collision given the known initial position
        # and velocity and see if they're positive and integral. If the are, that's the solution
        # print(rvx, rvy, rpx, rpy, t1, t2)
        if all(will_collide_at(hailstone, thrown) is not None for hailstone in hailstones):
            # print(thrown)
            # print(sum(thrown[0]))
            return thrown
        else:
            break
    return None

def main():
    # search = [(-3, 1)]
    s = 600
    search = dovetail(0, -s, s)
    with multiprocessing.Pool(8) as pool:
        for res in tqdm.tqdm(pool.imap(find, search, chunksize=1024), total=(s*2+1)**2):
            if res is not None:
                thrown = res
                print(thrown)
                print(sum(thrown[0]))
                return thrown

    
DEBUG = False

def debug(*args):
    if DEBUG:
        print(*args)

# logging.basicConfig()
# logging.getLogger().setLevel(logging.WARNING) #logging.DEBUG)
if __name__ == "__main__":
    main()
