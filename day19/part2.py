import sys
import re
import operator
import json
from functools import reduce

PATTERN1_1 = re.compile(r"^(\w+){(?:(\w+[<>]\d+:\w+(?:,\w+[<>]\d+:\w+)*),)?(\w+)}$")
PATTERN1_2 = re.compile(r"(\w+)([<>])(\d+):(\w+)")
PATTERN2 = re.compile(r"(\w+)=(\d+)")

workflows = {}
inputs = []
with open(sys.argv[1], 'r') as f:
    state = 0
    for line in f:
        line = line.strip()
        if state == 0:
            if not line:
                state = 1
                continue
            m = PATTERN1_1.match(line)
            workflow_name = m.group(1)
            terminal_state = m.group(3)
            rules = []
            inner = m.group(2)
            if inner:
                for m2 in PATTERN1_2.finditer(m.group(2)):
                    test_var = m2.group(1)
                    op = {'>': operator.gt, '<': operator.lt}[m2.group(2)]
                    test_val = int(m2.group(3))
                    test_dest = m2.group(4)
                    rules.append((test_var, op, test_val, test_dest))
            workflows[workflow_name] = (rules, terminal_state)
        else:
            if not line:
                break
            inputs.append({m.group(1): int(m.group(2)) for m in PATTERN2.finditer(line)})

class Range:
    def __init__(self, start, end):
        end = max(start, end)
        self.start = start
        self.end = end

    def __eq__(self, other):
        if not isinstance(other, Range):
            return NotImplemented
        return (self.start == other.start) and (self.end == other.end)

    def __hash__(self):
        return hash((self.start, self.end))

    def __bool__(self):
        return len(self) > 0

    def __len__(self):
        return self.end - self.start

    def __and__(self, other):
        if not isinstance(other, Range):
            return NotImplemented
        return Range(max(self.start, other.start), min(self.end, other.end))

    def __gt__(self, other):
        # TODO test logic
        if not isinstance(other, int):
            return NotImplemented
        return Range(max(other+1, self.start), self.end)

    def __lt__(self, other):
        # TODO test logic
        if not isinstance(other, int):
            return NotImplemented
        return Range(self.start, min(other, self.end))

    def __ge__(self, other):
        # TODO test logic
        if not isinstance(other, int):
            return NotImplemented
        return Range(max(other, self.start), self.end)

    def __le__(self, other):
        # TODO test logic
        if not isinstance(other, int):
            return NotImplemented
        return Range(self.start, min(other+1, self.end))

    def __repr__(self):
        return f'Range({self.start}, {self.end})'

    def __str__(self):
        return repr(self)
        

class _PBComparsion:
    def __init__(self, pb, var):
        self._pb = pb
        self._var = var

    def _compare(self, other, op):
        if not isinstance(other, int):
            return NotImplemented
        new_vals = []
        for v2r in self._pb._var_to_ranges:
            ranges = v2r[self._var]
            new_ranges = []
            for rng in ranges:
                new_rng = op(rng, other)
                if new_rng:
                    new_ranges.append(new_rng)
            new_pb = {
                **{
                    k: v
                    for k, v in v2r.items()
                    if k != self._var
                },
                self._var: new_ranges,
            }
            if PossibleValues([new_pb]):
                new_vals.append(new_pb)
        return PossibleValues(list(dedup(new_vals)))
                

    def __gt__(self, other):
        return self._compare(other, operator.gt)

    def __lt__(self, other):
        return self._compare(other, operator.lt)

    def __ge__(self, other):
        return self._compare(other, operator.ge)

    def __le__(self, other):
        return self._compare(other, operator.le)

def dedup(lst):
    seen = set()
    for x in lst:
        k = json.dumps(x, sort_keys=True, default=lambda x: x.__dict__)
        if k not in seen:
            seen.add(k)
            yield x

def overlaps(rngs1, rngs2):
    return any(
        any((rng1 & rng2) for rng2 in rngs2)
        for rng1 in rngs1
    )

class PossibleValues:
    def __init__(self, var_to_ranges):
        self._var_to_ranges = var_to_ranges

    @classmethod
    def empty(cls):
        return cls([])

    def __bool__(self):
        return len(self) > 0

    def __len__(self):
        return sum(reduce(lambda x, y: x * y, (
            sum(len(rng) for rng in rngs)
            for rngs in var_to_rng.values()
        )) for var_to_rng in self._var_to_ranges)

    def __getitem__(self, var):
        return _PBComparsion(self, var)

    def __or__(self, other):
        if not isinstance(other, PossibleValues):
            return NotImplemented
        if self._var_to_ranges == other._var_to_ranges:
            return self
        if not self:
            return other
        if not other:
            return self
        # All var sets in the union have to be disjoint for the whole thing to be joint
        disjoint = all(
            # if any axis is disjoint, the whole thing is disjoint
            any(not overlaps(self_v2r[v], other_v2r[v]) for v in 'xmas')
            for self_v2r in self._var_to_ranges
            for other_v2r in other._var_to_ranges
        )
        if disjoint:
            return PossibleValues(self._var_to_ranges + other._var_to_ranges)
        print(self)
        print(other)
        raise NotImplementedError

    def __repr__(self):
        return f'PossibleValues([{self._var_to_ranges!r}])'

    def __str__(self):
        return repr(self)

possible_values = PossibleValues([{var: [Range(1, 4001)] for var in 'xmas'}])

def get_accept_values(possible_values, state):
    if state == 'A':
        return possible_values
    elif state == 'R':
        return PossibleValues.empty()
    rules, terminal = workflows[state]
    out_pb = PossibleValues.empty()
    for var, op, val, dest in rules:
        in_pb = op(possible_values[var], val)
        inv_op = {
            operator.lt: operator.ge,
            operator.gt: operator.le,
        }[op]
        possible_values = inv_op(possible_values[var], val)
        if in_pb:
            out_pb |= get_accept_values(in_pb, dest)
    if possible_values:
        out_pb |= get_accept_values(possible_values, terminal)
    return out_pb
    
    
print(len(get_accept_values(possible_values, 'in')))

