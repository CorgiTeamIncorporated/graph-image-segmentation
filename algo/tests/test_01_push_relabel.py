import os
import time

import networkx as nx
from algo.graph_utils import get_max_flow
from networkx.algorithms.flow import preflow_push

from .utils import read_graph_from_file


def test_1_default_input():
    graph = nx.DiGraph()

    graph.add_nodes_from(list(range(1, 5)))
    graph.add_edge(1, 2, capacity=10000)
    graph.add_edge(1, 3, capacity=10000)
    graph.add_edge(2, 3, capacity=1)
    graph.add_edge(3, 4, capacity=10000)
    graph.add_edge(2, 4, capacity=10000)

    assert get_max_flow(graph, 1, 4, -1).graph['flow_value'] == 20000
    assert get_max_flow(graph, 1, 4, 0).graph['flow_value'] == 20000
    assert get_max_flow(graph, 1, 4, 1).graph['flow_value'] == 20000
    assert get_max_flow(graph, 1, 4, 2).graph['flow_value'] == 20000
    assert get_max_flow(graph, 1, 4, 3).graph['flow_value'] == 20000


def test_2_hand_crafted_tests():
    target_dir = './algo/tests/push_relabel_test_inputs'

    for filename in os.listdir(target_dir):
        file_path = os.path.join(target_dir, filename)
        graph = read_graph_from_file(file_path)
        nodes_quantity = len(graph)

        true_graph = preflow_push(graph, 1, nodes_quantity,
                                  value_only=True)

        timer_start = time.time()
        our_graph = get_max_flow(graph, 1, nodes_quantity,
                                 nodes_quantity//10)
        timer_end = time.time()

        true_max_flow = true_graph.graph['flow_value']
        our_max_flow = our_graph.graph['flow_value']
        assert true_max_flow == our_max_flow

        print()
        print('filename: ', filename)
        print('elapsed wall-clock time (s): ', timer_end - timer_start)
        print('max flow: ', our_max_flow)
