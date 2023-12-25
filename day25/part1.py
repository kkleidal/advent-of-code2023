import networkx as nx
import sys

def main():
    g = nx.Graph()

    with open(sys.argv[1], 'r') as f:
        for line in f:
            if (line := line.strip()):
                from_, to_ = line.split(": ")
                for dest in to_.split(" "):
                    g.add_edge(from_, dest)

    cut_edges = nx.minimum_edge_cut(g)
    g2 = g.copy()
    for edge in cut_edges:
        g2.remove_edge(*edge)
    ccs = list(nx.connected_components(g2))
    assert len(ccs) == 2
    return len(ccs[0]) * len(ccs[1])

if __name__ == '__main__':
    print(main())
