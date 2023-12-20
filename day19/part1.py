import sys
import re
import operator

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

def execute(workflows, inputs):
    state = 'in'
    while state not in ('A', 'R'):
        rules, terminal = workflows[state]
        found = False
        for var, op, val, dest in rules:
            if op(inputs[var], val):
                state = dest
                found = True
                break
        if not found:
            state = terminal
    return state == 'A'

print(sum(sum(inp.values()) for inp in inputs if execute(workflows, inp)))
