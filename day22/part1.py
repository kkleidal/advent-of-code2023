import sys
import string
import networkx as nx

def overlap(xs1, xs2, xo1, xo2):
    minn = max(xs1, xo1)
    maxx = min(xs2, xo2)
    if minn > maxx:
        return None
    return (minn, maxx)

class Block:
    def __init__(self, index, start, end):
        self.index = index
        start, end = sorted([start, end])
        self.start = start
        self.end = end
        self.orientation = tuple(1 if abs(e - s) > 0 else 0 for s, e in zip(start, end))
        if self.orientation == (0, 0, 0):
            # Arbitrary for cube
            self.orientation = (1, 0, 0)
        assert sum(self.orientation) == 1
        self.volume = sum(abs(e - s) + 1 for o, s, e in zip(self.orientation, start, end) if o)
        assert self.volume >= 1
        self.support_set = set()

    def __str__(self):
        return f'Block({index_to_letter(self.index)}: {self.start}, {self.end}; vol={self.volume}, ori={self.orientation})'
    
    def __repr__(self):
        return str(self)

    @property
    def min_z(self):
        return min(self.start[2], self.end[2])

    def z_support_for_other(self, other):
        (xs1, ys1, zs1) = self.start
        (xs2, ys2, zs2) = self.end
        (xo1, yo1, zo1) = other.start
        (xo2, yo2, zo2) = other.end
        x_overlap = overlap(xs1, xs2, xo1, xo2)
        if x_overlap is None:
            return None
        y_overlap = overlap(ys1, ys2, yo1, yo2)
        if y_overlap is None:
            return None
        if max(zs1, zs2) < min(zo1, zo2):
            return max(zs1, zs2) + 1
        elif max(zo1, zo2) < max(zs1, zs2):
            return None
        else:
            raise ValueError("Detected positional overlap")
    
    def will_support(self, other):
        return self.z_support_for_other(other) is not None

    def drop(self, possibly_below):
        max_support_z = 1
        max_support_set = set()
        for block in possibly_below:
            support_at = block.z_support_for_other(self)
            if support_at is not None:
                if support_at > max_support_z:
                    max_support_z = support_at
                    max_support_set = {block.index}
                elif support_at == max_support_z:
                    max_support_set.add(block.index)
                else:
                    ...
                    # below
        drop_dist = min(self.start[2], self.end[2]) - max_support_z
        self.start = (self.start[0], self.start[1], self.start[2] - drop_dist)
        self.end = (self.end[0], self.end[1], self.end[2] - drop_dist)
        self.support_set = max_support_set


def index_to_letter(index):
    out = ''
    alpha = string.ascii_lowercase.upper()
    while len(out) == 0 or index > 0:
        out = alpha[index % len(alpha)] + out
        index //= len(alpha)
    return out
    

supports = nx.DiGraph()

blocks = []
with open(sys.argv[1], 'r') as f:
    for line in f:
        block = Block(len(blocks), *(tuple(map(int,coord.split(','))) for coord in line.strip().split('~')))
        supports.add_node(len(blocks))
        blocks.append(block)

for i in range(len(blocks)):
    for j in range(0, len(blocks)):
        if i == j:
            continue
        if blocks[i].will_support(blocks[j]):
            supports.add_edge(i, j)

possibly_below = []
for i in list(nx.topological_sort(supports)):
    blocks[i].drop(possibly_below)
    possibly_below.append(blocks[i])


actually_supports = nx.DiGraph()
for i in range(len(blocks)):
    actually_supports.add_node(i)
for i in range(len(blocks)):
    for j in blocks[i].support_set:
        actually_supports.add_edge(j, i)

disintegratable = set()
for i in range(len(blocks)):
    supports = list([j for _, j in actually_supports.out_edges(i)])
    # If all the blocks this block supports are supported by another block, then this block
    # can be disintegrated
    if all(
        len(list(actually_supports.in_edges(j))) > 1
        for j in supports
    ):
        disintegratable.add(i)
print(len(disintegratable))
