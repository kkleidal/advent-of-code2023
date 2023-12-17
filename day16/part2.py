# Slow but didn't feel like optimizing, haha. It's amazing that a progress bar can make you more patient. 13 minutes.

import sys
from abc import ABC, abstractmethod
from typing import List
import numpy as np
from collections import defaultdict
from tqdm import tqdm


class Element(ABC):
    @abstractmethod
    def redirect_beam(self, direction: np.ndarray) -> List[np.ndarray]:
        ...

class Empty(Element):
    def redirect_beam(self, direction: np.ndarray) -> List[np.ndarray]:
        return [direction]

class Splitter(Element):
    def __init__(self, direction):
        self.direction = np.array([0, 1]) if direction == '-' else np.array([1, 0])

    def redirect_beam(self, direction: np.ndarray) -> List[np.ndarray]:
        d = np.dot(direction, self.direction)
        if d != 0:
            # pointy end
            return [direction]
        else:
            # split
            return [self.direction, -self.direction]

class Mirror(Element):
    def __init__(self, direction):
        self.direction = direction

    def redirect_beam(self, direction: np.ndarray) -> List[np.ndarray]:
        if self.direction == '/':
            return [(np.array([[0, -1], [-1, 0]]) @ np.expand_dims(direction, 1)).squeeze(1)]
        else:
            assert self.direction == '\\'
            return [(np.array([[0, 1], [1, 0]]) @ np.expand_dims(direction, 1)).squeeze(1)]


def get_element(c):
    if c == '.':
        return Empty()
    elif c in '-|':
        return Splitter(c)
    elif c in '/\\':
        return Mirror(c)
    else:
        assert False

rows = []
with open(sys.argv[1], 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            rows.append([get_element(c) for c in line])

def energizes(initial_pos, initial_vec):
    beams = {}
    beams[(initial_pos, initial_vec)] = 1
    energized = set()
    visited_states = set()
    while True:
        new_beams = defaultdict(int)
        old_visited_states = set(visited_states)
        for (pos, vel), count in beams.items():
            visited_states.add((pos, vel))
            pos = np.array(list(pos))
            vel = np.array(list(vel))
            i, j = pos
            energized.add((i, j))
            el = rows[i][j]
            for new_vel in el.redirect_beam(vel):
                new_pos = tuple((pos + new_vel).tolist())
                i, j = new_pos
                if i >= 0 and j >= 0 and i < len(rows) and j < len(rows[0]):
                    new_vel = tuple(new_vel.tolist())
                    new_beams[(new_pos, new_vel)] += count
        new_beams = dict(new_beams)
        beams = new_beams
        if visited_states == old_visited_states:
            break
    return len(energized)

N = len(rows)
M = len(rows[0])
start_positions = [
    *[
        ((i, 0), (0, 1))
        for i in range(N)
    ],
    *[
        ((i, M-1), (0, -1))
        for i in range(len(rows))
    ],
    *[
        ((0, j), (1, 0))
        for j in range(M)
    ],
    *[
        ((N-1, j), (-1, 0))
        for j in range(M)
    ],
]

print(max(energizes(*conf) for conf in tqdm(start_positions)))


