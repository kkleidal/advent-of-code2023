import sys
import networkx as nx

node_to_type = {}
with open(sys.argv[1], 'r') as f:
    i = 0
    for line in f:
        line = line.strip()
        if line:
            for j, c in enumerate(line):
                if c in ('.', '<', '>', 'v', '^'):
                    node_to_type[(i, j)] = c
            i += 1

directions = [
    (1, 0),
    (0, 1),
    (0, -1),
    (-1, 0),
]
carrets = 'v><^'
carret_to_direction = {k: v for k, v in zip(carrets, directions)}

N = max(i for i, _ in node_to_type) + 1
M = max(j for _, j in node_to_type) + 1

g = nx.DiGraph()
for (i, j), c in node_to_type.items():
    g.add_node((i, j))
    
for (i, j), c in node_to_type.items():
    if c == '.':
        for (di, dj) in directions:
            ii, jj = i + di, j + dj
            cc = node_to_type.get((ii, jj), '#')
            if cc == '.':
                g.add_edge((i, j), (ii, jj))
    elif c in carrets:
        di, dj = carret_to_direction[c]
        prev_node = (i - di, j - dj)
        next_node = (i + di, j + dj)
        assert node_to_type.get(prev_node) == '.'
        assert node_to_type.get(next_node) == '.'
        g.add_edge(prev_node, (i, j))
        g.add_edge((i, j), next_node)

start = min(node_to_type)
end = max(node_to_type)

# print([len(path) - 1 for path in nx.all_simple_paths(g, start, end)])
print(max(len(path) - 1 for path in nx.all_simple_paths(g, start, end)))
