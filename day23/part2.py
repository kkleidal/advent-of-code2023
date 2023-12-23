import sys
import networkx as nx
from collections import deque

# Parse:
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

# Build graph (logic is a little overly complicated being that carrets don't mean
# anything for part 2, but I copied code from part1 and modified it):
g = nx.Graph()
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

# Condense long straightaway stretches with no decisions into single edges with
# weights equal to path length, to decrease size of graph / simplify for next algorithm
g_landmark = nx.Graph()
landmark_nodes = set()
degrees = {n: d for n, d in g.degree()}
for node in g.nodes():
    if node == start or node == end or degrees[node] > 2:
        g_landmark.add_node(node)
        landmark_nodes.add(node)
for node1 in landmark_nodes:
    for edge1 in nx.edges(g, node1):
        node2 = min(set(edge1) - {node1})
        seen = {node1, node2}
        path_weight = 1
        while node2 not in landmark_nodes:
            edges = [edge for edge in nx.edges(g, node2) if set(edge) - seen]
            assert len(edges) == 1
            edge2 = edges[0]
            node3 = min(set(edge2) - seen)
            seen.add(node3)
            path_weight += 1
            node2 = node3
        assert node1 in landmark_nodes
        assert node2 in landmark_nodes
        g_landmark.add_edge(node1, node2, weight=path_weight)

g = g_landmark

def max_path_length(g, start, end):
    # Find the max path length by breaking up the graph into more reasonable subproblems.
    # Imagine a graph that's a bunch of cycles in a line connected by edges, like:
    # -O-O-O-O-O-O-O- ...
    # There will be 2^(# of circles) possible paths. If, however, we recognize that all
    # paths must go through the edges between the circles, we can break the problem up by
    # computing the longest path for each circle (say: the top arc might be longer than the
    # bottom arc, or vise versa), and then adding the max length paths of the subproblems together.
    # We generalize this by finding nodes in the graph that we can remove that will disconnect
    # the start and end nodes. These are critical "cutting points" that we can use to split up
    # the problem into smaller sub problems.
    cuttable_nodes = []
    for node in nx.nodes(g):
        if node == start or node == end:
            continue
        g2 = g.copy()
        for edge in list(g2.edges(node)):
            g2.remove_edge(*edge)
        g2.remove_node(node)
        if not nx.has_path(g2, start, end):
            print(f"Found cut {node}")
            ccs = list(nx.connected_components(g2))
            assert len(ccs) == 2
            sub_problems = []
            for cc in ccs:
                g_sub = g.copy()
                for n in cc:
                    g_sub.remove_node(n)
                remaining = set(g_sub.nodes())
                if start in remaining:
                    sub_start = start
                    sub_end = node
                else:
                    sub_start = node
                    sub_end = end
                assert sub_start in remaining
                assert sub_end in remaining
                print(f"Cut {sub_start} -> {sub_end}. Size: {len(remaining)}")
                sub_problems.append((g_sub, sub_start, sub_end, len(remaining)))
            cuttable_nodes.append((max(s[3] for s in sub_problems), node, sub_problems))
    if cuttable_nodes:
        _, cut_node, sub_problems = min(cuttable_nodes)
        combined = 0
        for g_sub, sub_start, sub_end, _ in sub_problems:
            out = max_path_length(g_sub, sub_start, sub_end)
            combined += out
        return combined
    else:
        print(f"Solving {start} -> {end} outright")
        return max(nx.path_weight(g, path, weight="weight") for path in nx.all_simple_paths(g, start, end))

print(max_path_length(g, start, end))
