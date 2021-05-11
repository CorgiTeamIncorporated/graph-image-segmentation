import networkx as nx
import time
import os
from networkx.algorithms.flow import preflow_push
from push_relabel import get_max_flow


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


def test_2_hand_crafted_tests():
    target_dir = os.path.join(os.getcwd(), 'tests\\push_relabel_test_inputs')

    for filename in os.listdir(target_dir):
        file_path = os.path.join(target_dir, filename)
        graph = read_graph_from_file(file_path)
        nodes_quantity = len(graph)

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
