import networkx as nx
import random
from networkx.algorithms.flow import preflow_push
from push_relabel import get_max_flow


def test_1_default_input():
    graph = nx.DiGraph()

    graph.add_nodes_from(list(range(1, 5)))
    graph.add_edge(1, 2, capacity=10000)
    graph.add_edge(1, 3, capacity=10000)
    graph.add_edge(2, 3, capacity=1)
    graph.add_edge(3, 4, capacity=10000)
    graph.add_edge(2, 4, capacity=10000)

    assert get_max_flow(graph, 1, 4, -1) == 20000
    assert get_max_flow(graph, 1, 4, 0) == 20000
    assert get_max_flow(graph, 1, 4, 1) == 20000
    assert get_max_flow(graph, 1, 4, 2) == 20000
    assert get_max_flow(graph, 1, 4, 3) == 20000


def test_2_brute_force_input():
    for seed in range(0, 100):
        for size in range(2, 100):
            # generate random DiGraph
            graph = nx.scale_free_graph(n=size, alpha=0.15,
                                        beta=0.7, gamma=0.15, seed=seed)
            graph = nx.DiGraph(graph)

            # init random capacity to edges
            dict_of_weights = {'capacity': random.random()}
            dict_of_edges_weights = {e:  dict_of_weights for e in graph.edges}
            nx.set_edge_attributes(graph, dict_of_edges_weights)

            # calculate max flow value
            true_max_flow = preflow_push(graph, 0, size-1, value_only=True)
            out_max_flow = get_max_flow(graph, 0, size-1, 3)

            assert true_max_flow.graph['flow_value'] == out_max_flow
