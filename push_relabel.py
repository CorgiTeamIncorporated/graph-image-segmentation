import networkx as nx
from typing import Optional


class PushRelabelAlgorithm:
    def __init__(self, graph: nx.DiGraph, source: int, sink: int) -> None:
        self.source: int = source
        self.sink: int = sink
        self._build_residual_network(graph)

    def _build_residual_network(self, graph: nx.DiGraph) -> None:
        self.graph: nx.DiGraph = nx.DiGraph()

        for node in graph.nodes:
            self.graph.add_node(node, excess=0, height=0)

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
                self.push(u, v, flow)

    def _residual_capacity(self, u: int, v: int) -> int:
        edge_data: dict = self.graph.edges[(u, v)]
        return edge_data['capacity'] - edge_data['flow']

    def push(self, u: int, v: int, delta: Optional[int] = None) -> None:
        delta = delta or min(self.graph.nodes[u]['excess'],
                             self._residual_capacity(u, v))

        self.graph[u][v]['flow'] += delta
        self.graph[v][u]['flow'] -= delta
        self.graph.nodes[u]['excess'] -= delta
        self.graph.nodes[v]['excess'] += delta

    def relabel(self, u: int) -> None:
        min_height: int = min(self.graph.nodes[v]['height']
                              for v in self.graph.neighbors(u)
                              if self._residual_capacity(u, v) > 0)
        self.graph.nodes[u]['height'] = min_height + 1
