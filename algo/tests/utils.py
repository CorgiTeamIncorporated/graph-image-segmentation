import networkx as nx


def read_graph_from_file(file_path: str) -> nx.DiGraph:
    graph = nx.DiGraph()

    with open(file_path, 'r') as f:
        init_input = f.readline().split()
        nodes_quantity, _ = list(map(int, init_input))

        graph.add_nodes_from(list(range(1, nodes_quantity + 1)))

        for line in f:
            edge_input = line.split()
            u, v, capacity = list(map(int, edge_input))
            graph.add_edge(u, v, capacity=capacity)

    return graph
