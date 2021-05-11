from collections import deque
from typing import Deque, Dict, List, Optional, Tuple, Union


import networkx as nx

__all__ = ['get_max_flow']

# Applicable types for edges capacities
numeric = Union[int, float]


def get_max_flow(graph: nx.DiGraph, source: int, sink: int,
                 global_relabel_freq: int = 100) -> numeric:
    """
        Calculate maximum flow of graph.
        Push-relabel algorithm with highest label selection rule is used.

        Parameters
        ----------
        graph : nx.Graph
            Graph to find maximum flow in.
        source : int
            Source of flow.
        sink : int
            Sink of flow.
        global_relabel_freq : int
            Number of push-relabel operations between global relabelings.
            If it is less than 1, global relabelings will not be used.

        Returns
        -------
        flow_value : numeric
            Value of the maximum flow.
    """

    # Number of nodes in the graph
    nodes_num: int = graph.order()

    # State of the algorithm
    active_nodes: List[set] = [set() for _ in range(2 * nodes_num)]

    # Residual network of the algorithm
    network: nx.DiGraph = graph.copy()

    # Push-relabel counter
    operation_counter: int = global_relabel_freq

    def get_height(u: int) -> int:
        return network.nodes[u]['height']

    def get_excess(u: int) -> numeric:
        return network.nodes[u]['excess']

    def get_residual_capacity(u: int, v: int) -> numeric:
        return network[u][v]['capacity'] - network[u][v]['flow']

    def is_push_allowed(u: int, v: int) -> bool:
        return (get_excess(u) > 0 and
                get_height(u) == get_height(v) + 1)

    def build_residual_network() -> None:
        """
            Initialize algorithm by building residual network.
            Initial flow and nodes heights are also set here.

            Parameters
            ----------
            None.

            Returns
            -------
            None.
        """

        nonlocal network

        new_graph: nx.DiGraph = nx.DiGraph()

        for node in network.nodes:
            new_graph.add_node(node, excess=0, height=0)

        new_graph.nodes[source]['height'] = nodes_num

        for (u, v), edge_data in network.edges.items():
            capacity = edge_data['capacity']

            if not new_graph.has_edge(u, v):
                new_graph.add_edge(u, v, capacity=capacity, flow=0)
                new_graph.add_edge(v, u, capacity=0, flow=0)
            else:
                new_graph[u][v]['capacity'] = capacity

        network = new_graph.copy()

        for u, v in new_graph.edges(source):
            flow = new_graph[u][v]['capacity']
            if flow > 0:
                push(u, v, flow)

    def push(u: int, v: int, delta: Optional[numeric] = None) -> None:
        """
            Apply push operation to node.

            Parameters
            ----------
            u : int
                Source node to apply operation to.
            v : int
                Destination node to apply operation to.
            delta : numeric
                Value of flow to push.
                Maximum possible value will be chosen if not specified.

            Returns
            -------
            None.
        """

        delta = delta or min(get_excess(u),
                             get_residual_capacity(u, v))

        if v not in (source, sink) and get_excess(v) == 0 and delta > 0:
            height = get_height(v)
            active_nodes[height].add(v)

        network[u][v]['flow'] += delta
        network[v][u]['flow'] -= delta
        network.nodes[u]['excess'] -= delta
        network.nodes[v]['excess'] += delta

        if get_excess(u) == 0:
            height = get_height(u)
            active_nodes[height].remove(u)

    def relabel(u: int) -> None:
        """
            Apply relabel operation to node.

            Parameters
            ----------
            u : int
                Node to apply operation to.

            Returns
            -------
            None.
        """

        old_height: int = get_height(u)

        new_height: int = min(get_height(v)
                              for v in network.neighbors(u)
                              if get_residual_capacity(u, v) > 0) + 1
        network.nodes[u]['height'] = new_height

        if old_height != new_height:
            active_nodes[new_height].add(u)
            active_nodes[old_height].remove(u)

    def discharge(u: int) -> None:
        """
            Apply push and relabel operations until node excess become zero.

            Parameters
            ----------
            u : int
                Graph node to apply operations to.

            Returns
            -------
            None.
        """

        nonlocal operation_counter

        while get_excess(u) > 0:
            for v in network.neighbors(u):
                if is_push_allowed(u, v):
                    push(u, v)
                    operation_counter += 1

            if get_excess(u) > 0:
                relabel(u)
                operation_counter += 1

    def choose_next_node() -> Union[int, None]:
        """
            Choose next node to discharge using highest label selection rule.
            If no active node found, None is returned.

            Parameters
            ----------
            None.

            Returns
            -------
            node : int
                Next node or None.
        """

        nonlocal operation_counter

        max_height = len(active_nodes)

        if (global_relabel_freq > 0 and
                operation_counter >= global_relabel_freq):
            operation_counter = 0
            max_height = global_relabel()

        for node_set in reversed(active_nodes[:max_height+1]):
            if len(node_set) != 0:
                return next(iter(node_set))

        return None

    def reverse_bfs(src: int) -> Dict[int, int]:
        """
            Perform a reverse breadth-first search from src in the residual
            network.

            Parameters
            ----------
            src : int
                Source node to apply operation to.

            Returns
            -------
            heights : dict
                Dictionary of nodes with their heights.
        """

        heights: Dict[int, int] = {src: 0}
        queue: Deque[Tuple[int, int]] = deque([(src, 0)])

        while len(queue) > 0:
            u, height = queue.popleft()
            height += 1

            for v in network.pred[u]:
                if v not in heights and get_residual_capacity(v, u) > 0:
                    heights[v] = height
                    queue.append((v, height))

        return heights

    def global_relabel() -> int:
        """
            Apply the global relabeling heuristic.

            Parameters
            ----------
            None.

            Returns
            -------
            max_height : int
                Max node height in residual flow.
        """

        heights: Dict[int, int] = reverse_bfs(sink)
        max_height = max(heights.values())

        # Mark nodes from which sink is unreachable in residual flow.
        for u, node_data in network.nodes.items():
            if u not in heights and node_data['height'] < nodes_num:
                heights[u] = nodes_num + 1

        del heights[sink]

        for u, new_height in heights.items():
            old_height = network.nodes[u]['height']

            if new_height != old_height:
                if get_excess(u) > 0:
                    active_nodes[old_height].remove(u)
                    active_nodes[new_height].add(u)

                network.nodes[u]['height'] = new_height

        return max_height

    build_residual_network()

    while node := choose_next_node():
        discharge(node)

    return get_excess(sink)
