import sys
import re
from typing import Iterable, Tuple, List
from abc import ABC, abstractmethod
from collections import deque, defaultdict

PATTERN1 = re.compile(r"^(%|&)?(\w+) -> (.*)$")


class Node(ABC):
    def __init__(self, dests):
        self.dests = dests

    @abstractmethod
    def send(self, src: str, signal: bool) -> Iterable[Tuple[str, bool]]:
        ...

    def set_inputs(self, src: List[str]):
        ...


class Broadcaster(Node):
    def send(self, src: str, signal: bool) -> Iterable[Tuple[str, bool]]:
        for dest in self.dests:
            yield (dest, signal)


class FlipFlop(Node):
    def __init__(self, dests):
        super().__init__(dests)
        self.state = False

    def send(self, src: str, signal: bool) -> Iterable[Tuple[str, bool]]:
        if not signal:
            self.state = not self.state
            send = self.state
            for dest in self.dests:
                yield (dest, send)


class Conjunction(Node):
    def __init__(self, dests):
        super().__init__(dests)
        self.memory = {}

    def send(self, src: str, signal: bool) -> Iterable[Tuple[str, bool]]:
        self.memory[src] = signal
        send = not all(self.memory.values())
        for dest in self.dests:
            yield (dest, send)

    def set_inputs(self, src: List[str]):
        for s in src:
            self.memory[s] = False

    

name_to_node = {}
with open(sys.argv[1], 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            m = PATTERN1.match(line)
            prefix = m.group(1)
            name = m.group(2)
            dests = m.group(3).split(', ')
            node = {
                None: Broadcaster,
                '%': FlipFlop,
                '&': Conjunction,
            }[prefix](dests)
            name_to_node[name] = node
name_to_inputs = defaultdict(set)
for src, node in name_to_node.items():
    for dest in node.dests:
        name_to_inputs[dest].add(src)
for dest, srcs in name_to_inputs.items():
    if dest in name_to_node:
        name_to_node[dest].set_inputs(srcs)

def push(times=1, debug=False):
    high = 0
    low = 0
    for _ in range(times):
        event_queue = deque([('button', 'broadcaster', False)])
        while event_queue:
            src, dest, signal = event_queue.popleft()
            if debug:
                print(f'{src} -{"high" if signal else "low"} -> {dest}')
            if signal:
                high += 1
            else:
                low += 1
            if dest not in name_to_node:
                continue
            for evt in name_to_node[dest].send(src, signal):
                event_queue.append((dest, *evt))
        if debug:
            print(high, low)
            print()
    return (high, low)

high, low = push(1000)
print(high * low)
