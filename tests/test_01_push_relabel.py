import networkx as nx
from push_relabel import get_max_flow


def test_1():
    graph = nx.DiGraph()

    graph.add_nodes_from(list(range(1, 5)))
    graph.add_edge(1, 2, capacity=10000)
    graph.add_edge(1, 3, capacity=10000)
    graph.add_edge(2, 3, capacity=1)
    graph.add_edge(3, 4, capacity=10000)
    graph.add_edge(2, 4, capacity=10000)

    assert get_max_flow(graph, 1, 4, 2) == 20000
