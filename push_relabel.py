import networkx as nx


class PushRelabelAlgorithm:
    def __init__(self, graph: nx.DiGraph, source: int, sink: int) -> None:
        self.graph: nx.DiGraph = graph.copy()
        self.source: int = source
        self.sink: int = sink

        source_data: dict = self.graph.nodes[source]

        for _, node_data in self.graph.nodes.items():
            node_data['height'] = 0
            node_data['excess'] = 0

        source_data['height'] = self.graph.order()

        for _, edge_data in self.graph.edges.items():
            edge_data['flow'] = 0

        for edge in self.graph.edges(source):
            edge_data = self.graph.edges[edge]
            target_data = self.graph.nodes[edge[1]]

            edge_data['flow'] = edge_data['capacity']
            source_data['excess'] -= edge_data['capacity']
            target_data['excess'] += edge_data['capacity']

    def _residual_capacity(self, u: int, v: int) -> int:
        edge_data = self.graph.edges[(u, v)]
        return edge_data['capacity'] - edge_data['flow']

    def push(self, u: int, v: int) -> None:
        u_data: dict = self.graph.nodes[u]
        v_data: dict = self.graph.nodes[v]
        edge_data: dict = self.graph.edges[(u, v)]

        delta = min(u_data['excess'],
                    self._residual_capacity(u, v))

        edge_data['flow'] += delta
        u_data['excess'] -= delta
        v_data['excess'] += delta

    def relabel(self, u: int) -> None:
        min_height = min(self.graph.nodes[v]['height']
                         for v in self.graph.neighbors(u)
                         if self._residual_capacity(u, v) > 0)
        self.graph.nodes[u]['height'] = min_height + 1
