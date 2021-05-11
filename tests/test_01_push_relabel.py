import networkx as nx
import random
import time
import os
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


# def test_2_brute_force_input():
#     for seed in range(0, 100):
#         for size in range(2, 100):
#             # generate random DiGraph
#             graph = nx.scale_free_graph(n=size, alpha=0.15,
#                                         beta=0.7, gamma=0.15, seed=seed)
#             graph = nx.DiGraph(graph)

#             # init random capacity to edges
#             dict_of_weights = {'capacity': random.random()}
#             dict_of_edges_weights = {e:  dict_of_weights for e in graph.edges}
#             nx.set_edge_attributes(graph, dict_of_edges_weights)

#             # calculate max flow value
#             true_max_flow = preflow_push(graph, 0, size-1, value_only=True)
#             out_max_flow = get_max_flow(graph, 0, size-1, 3)

#             assert true_max_flow.graph['flow_value'] == out_max_flow


def test_3_hand_crafted_tests():
    target_dir = os.path.join(os.getcwd(), 'tests\\push_relabel_test_inputs')

    for filename in os.listdir(target_dir):
        with open(os.path.join(target_dir, filename), 'r') as f:
            init_input = f.readline().split()
            nodes_quantity, edges_quantity = list(map(int, init_input))

            graph = nx.DiGraph()
            graph.add_nodes_from(list(range(1, nodes_quantity + 1)))

            for line in f:
                edge_input = line.split()
                u, v, capacity = list(map(int, edge_input))
                graph.add_edge(u, v, capacity=capacity)

            true_max_flow = preflow_push(graph, 1, nodes_quantity,
                                         value_only=True)

            timer_start = time.time()
            our_max_flow = get_max_flow(graph, 1, nodes_quantity,
                                        nodes_quantity//10)
            timer_end = time.time()

            assert true_max_flow.graph['flow_value'] == our_max_flow

            print()
            print('filename: ', filename)
            print('elapsed wall-clock time (s): ', timer_end - timer_start)
            print('max flow: ', our_max_flow)
