import os
from .utils import read_graph_from_file
from push_relabel import get_max_flow


def test_1_hand_crafted_tests():
    target_dir = './tests/push_relabel_test_inputs'

    for filename in os.listdir(target_dir):
        file_path = os.path.join(target_dir, filename)
        graph = read_graph_from_file(file_path)
        nodes_quantity = len(graph)

        graph = get_max_flow(graph, 1, nodes_quantity,
                             nodes_quantity//10, value_only=False)

        min_cut_value = 0
        for node in graph.graph['s_cut']:
            for u, v, attr in graph.out_edges(node, data=True):
                if v not in graph.graph['s_cut']:
                    min_cut_value += attr['capacity']

        assert min_cut_value == graph.graph['flow_value']
