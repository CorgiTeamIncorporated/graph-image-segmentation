from typing import Optional, List

import networkx as nx


class PushRelabelAlgorithm:
    def __init__(self, graph: nx.DiGraph, source: int, sink: int) -> None:
        N: int = graph.order()
        self.source: int = source
        self.sink: int = sink
        self._active_nodes: List[set] = [set() for _ in range(2 * N)]
        self._inactive_nodes: List[set] = [set() for _ in range(2 * N)]
        self._build_residual_network(graph)

    def _build_residual_network(self, graph: nx.DiGraph) -> None:
        self.graph: nx.DiGraph = nx.DiGraph()

        for node in graph.nodes:
            self.graph.add_node(node, excess=0, height=0)
            if node != self.source and node != self.sink:
                self._inactive_nodes[0].add(node)

        self.graph.nodes[self.source]['height'] = self.graph.order()

        for (u, v), edge_data in graph.edges.items():
            capacity = edge_data['capacity']

            if not self.graph.has_edge(u, v):
                self.graph.add_edge(u, v, capacity=capacity, flow=0)
                self.graph.add_edge(v, u, capacity=0, flow=0)
            else:
                self.graph[u][v]['capacity'] = capacity

        for u, v in self.graph.edges(self.source):
            flow = self.graph[u][v]['capacity']
            if flow > 0:
                self._push(u, v, flow)

    def _height(self, u: int) -> int:
        return self.graph.nodes[u]['height']

    def _excess(self, u: int) -> int:
        return self.graph.nodes[u]['excess']

    def _flow(self, u: int, v: int) -> int:
        return self.graph[u][v]['flow']

    def _capacity(self, u: int, v: int) -> int:
        return self.graph[u][v]['capacity']

    def _residual_capacity(self, u: int, v: int) -> int:
        return self._capacity(u, v) - self._flow(u, v)

    def _is_push_allowed(self, u: int, v: int) -> bool:
        return (self._excess(u) > 0 and
                self._height(u) == self._height(v) + 1)

    def _push(self, u: int, v: int, delta: Optional[int] = None) -> None:
        delta = delta or min(self._excess(u),
                             self._residual_capacity(u, v))

        if v != self.source and v != self.sink and self._excess(v) == 0 and delta > 0:
            height = self._height(v)
            self._active_nodes[height].add(v)
            self._inactive_nodes[height].remove(v)

        self.graph[u][v]['flow'] += delta
        self.graph[v][u]['flow'] -= delta
        self.graph.nodes[u]['excess'] -= delta
        self.graph.nodes[v]['excess'] += delta

        if self._excess(u) == 0:
            height = self._height(u)
            self._inactive_nodes[height].add(u)
            self._active_nodes[height].remove(u)

    def _is_relabel_allowed(self, u: int) -> bool:
        return (self._excess(u) > 0 and
                all(self._height(u) <= self._height(v)
                    for v in self.graph.neighbors(u)
                    if self._residual_capacity(u, v) > 0))

    def _relabel(self, u: int) -> None:
        old_height: int = self._height(u)

        new_height: int = min(self._height(v)
                              for v in self.graph.neighbors(u)
                              if self._residual_capacity(u, v) > 0) + 1
        self.graph.nodes[u]['height'] = new_height

        if old_height != new_height:
            if self._excess(u) == 0:
                self._inactive_nodes[new_height].add(u)
                self._inactive_nodes[old_height].remove(u)
            else:
                self._active_nodes[new_height].add(u)
                self._active_nodes[old_height].remove(u)

    def discharge(self, u: int) -> None:
        while self._excess(u) > 0:
            for v in self.graph.neighbors(u):
                if self._is_push_allowed(u, v):
                    self._push(u, v)

            self._relabel(u)

    def get_max_flow(self) -> int:
        active_node_found = True

        while active_node_found:
            active_node_found = False

            for node_set in reversed(self._active_nodes):
                if len(node_set) != 0:
                    active_node_found = True
                    self.discharge(next(iter(node_set)))
                    break

        return self._excess(self.sink)
