import sys
import heapq
import networkx as nx
import math
from tqdm import tqdm

rows = []
with open(sys.argv[1], 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            rows.append(list(map(int, line)))

print("Building graph")
N = len(rows)
M = len(rows[0])
directions = [
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1)
]
full_graph = nx.DiGraph()
for i in range(N):
    for j in range(M):
        for direction in directions:
            for time_in_direction in range(4):
                full_graph.add_node((i, j, direction, time_in_direction))

# Construct hypergraph
for i in range(N):
    for j in range(M):
        for direction in directions:
            for time_in_direction in range(11):
                for new_direction in directions:
                    if new_direction == direction and time_in_direction == 10:
                        continue
                    if new_direction == (-direction[0], -direction[1]):
                        continue
                    if new_direction != direction and time_in_direction < 4:
                        continue
                    npos = (i + new_direction[0], j + new_direction[1])
                    ntime_in_direction = (time_in_direction + 1) if direction == new_direction else 1
                    if not (npos[0] >= 0 and npos[0] < N and npos[1] >= 0 and npos[1] < M):
                        continue
                    full_graph.add_edge(
                        (i, j, direction, time_in_direction),
                        (*npos, new_direction, ntime_in_direction),
                        weight=rows[npos[0]][npos[1]],
                    )

print(full_graph)
print("Searching")
best = []
for direction in [(0, 1), (1, 0)]:
    paths = nx.algorithms.single_source_dijkstra_path_length(
        full_graph,
        source=(0, 0, direction, 0),
    )
    paths = {node: dist for node, dist in paths.items() if node[0:2] == (N-1, M-1) and node[3] >= 4}
    if len(paths) == 0:
        continue
    best_for_direction = min(dist for node, dist in paths.items())
    best.append(best_for_direction)

# Answer: 866
# Answer 1010
assert len(best) > 0
print(min(best))
