import sys
import re
import networkx as nx
import math
from typing import Iterable, Tuple, List
from abc import ABC, abstractmethod
from collections import deque, defaultdict

PATTERN1 = re.compile(r"^(%|&)?(\w+) -> (.*)$")


class Node(ABC):
    def __init__(self, dests):
        self.dests = dests
        self.reset_state()

    @abstractmethod
    def send(self, src: str, signal: bool) -> Iterable[Tuple[str, bool]]:
        ...

    def reset_state(self):
        ...
    
    def get_state(self):
        return None

    def set_inputs(self, src: List[str]):
        ...


class Broadcaster(Node):
    def send(self, src: str, signal: bool) -> Iterable[Tuple[str, bool]]:
        for dest in self.dests:
            yield (dest, signal)


class FlipFlop(Node):
    def reset_state(self):
        self.state = False

    def get_state(self):
        return self.state

    def send(self, src: str, signal: bool) -> Iterable[Tuple[str, bool]]:
        if not signal:
            self.state = not self.state
            send = self.state
            for dest in self.dests:
                yield (dest, send)


class Conjunction(Node):
    memory = {}

    def reset_state(self):
        self.memory = {k: False for k in self.memory}

    def get_state(self):
        return tuple(v for _, v in sorted(self.memory.items()))

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

def get_state():
    return tuple(
        state
        for state in (
            node.get_state()
            for name, node in sorted(name_to_node.items())
        ) if state is not None
    )

def get_upstream_nodes(dest):
    q = deque([dest])
    seen = {dest}
    while q:
        cur = q.popleft()
        for neighbor in name_to_inputs.get(cur, []):
            if neighbor not in seen:
                seen.add(neighbor)
                q.append(neighbor)
    return [name_to_node[name] for name in sorted(seen)]
    
def push(target='rx', expect=False):
    high = 0
    low = 0
    button_presses = 0
    seen = {}

    emission_history = []
    emissions = []
    states = {}

    for node in name_to_node.values():
        node.reset_state()
    upstream_nodes = get_upstream_nodes(target)

    while True: 
        state = get_state()
        if state in seen:
            raise ValueError(f"Cycle detected at {button_presses}")
        else:
            seen[state] = button_presses

        event_queue = deque([('button', 'broadcaster', False)])
        button_presses += 1
        while event_queue:
            src, dest, signal = event_queue.popleft()
            if src == target and (len(emission_history) == 0 or emission_history[-1] != button_presses):
                emission_history.append(button_presses)
                emissions.append(signal)
                state = tuple(node.get_state() for node in upstream_nodes)
                if state not in states:
                    states[state] = button_presses
                else:
                    cycle_len = button_presses - states[state]
                    hits = {(time, cycle_len) for sig, time in zip(emissions, emission_history) if sig == expect}
                    return hits
            if signal:
                high += 1
            else:
                low += 1
            if dest not in name_to_node:
                continue
            for evt in name_to_node[dest].send(src, signal):
                event_queue.append((dest, *evt))

def all_hit(a, b):
    out = set()
    for aa in a:
        for bb in b:
            common = combine_cycles_from_day8([aa, bb])
            assert (common[0] - aa[0]) % aa[1] == 0
            assert (common[0] - bb[0]) % bb[1] == 0
            out.add(common)
    return out


def combine_cycles_from_day8(cycles):
    a, n = cycles[0]
    for b, m in cycles[1:]:
        lcm = math.lcm(n, m)
        x = ((pow(n, -1, m) * (b - a)) % m) * n + a
        assert (x - a) % n == 0
        assert (x - b) % m == 0
        a = x
        n = lcm
    return a, n

def get_time(target, expect=False):
    if expect:
        if target == 'rx':
            assert len(name_to_inputs[target]) == 1
            return get_time(min(name_to_inputs[target]))
        else:
            return push(target, expect=expect)
    else:
        if all(isinstance(name_to_node[src], Conjunction) for src in name_to_inputs[target]):
            all_hits = None
            my_hits = []
            for src in name_to_inputs[target]:
                hits = get_time(src, expect=(not expect))
                my_hits.append(hits)
            for src, hits in zip(name_to_inputs[target], my_hits):
                if all_hits is None:
                    all_hits = hits
                else:
                    all_hits = all_hit(hits, all_hits)
            assert len(all_hits) == 1, "Only verified implementation for 1"
            a, n = min(all_hits)
            for hits in my_hits:
                assert len(hits) == 1
                b, m = min(hits)
                assert (a - b) % m == 0, f'{b} {m}'
            return all_hits
        else:
            return push(target, expect=expect)
    
out = get_time('rx', True)
assert len(out) == 1
print(min(out)[0])
# 225872806380073

