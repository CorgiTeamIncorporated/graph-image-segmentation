from itertools import product
from math import dist, exp, log
from typing import Callable, Dict, Iterable, Literal, NewType, Tuple

import networkx as nx
from PIL import Image
from algo.graph_utils import get_max_flow

Point = NewType('Point', Tuple[int, int])
PointType = Literal['object', 'background']

BoundaryCostFunction = Callable[[int, int, Point, Point], float]

RelativeCostFunction = Callable[[int, PointType], float]
RelativeCostGenerator = Callable[[Image.Image,
                                  Iterable[Point],
                                  Iterable[Point],
                                  float],
                                 RelativeCostFunction]


def gaussian(sigma: float) -> BoundaryCostFunction:
    def inner(i_p: int, i_q: int, p: Point, q: Point) -> float:
        return exp(-(i_p - i_q) ** 2 / (2 * sigma ** 2)) / dist(p, q)

    return inner


def histogram_cost(image: Image.Image,
                   object_points: Iterable[Point],
                   background_points: Iterable[Point],
                   infinity: float = 1e6) -> RelativeCostFunction:
    object_histogram: Dict[int, int] = dict()
    background_histogram: Dict[int, int] = dict()

    object_num = len(object_points)
    background_num = len(background_points)

    for point in object_points:
        pixel = image.getpixel(point)
        object_histogram[pixel] = object_histogram.get(pixel, 0) + 1

    for point in background_points:
        pixel = image.getpixel(point)
        background_histogram[pixel] = background_histogram.get(pixel, 0) + 1

    def inner(intensity: int, point_type: PointType) -> float:
        if point_type == 'object':
            freq = object_histogram.get(intensity, 0) / object_num
        elif point_type == 'background':
            freq = background_histogram.get(intensity, 0) / background_num

        if freq == 0.0:
            return infinity

        return -log(freq)

    return inner


class Segmentator:
    def __init__(self,
                 image: Image.Image,
                 neighbors: int = 4,
                 lambda_: float = 1.0,
                 boundary_cost: BoundaryCostFunction = gaussian(1.0),
                 relative_cost_gen: RelativeCostGenerator = histogram_cost):
        deltas_dict = {
            4: [x for x in product((-1, 1), repeat=2)],
            8: [x for x in product((-1, 0, 1), repeat=2) if x != (0, 0)]
        }

        assert neighbors in deltas_dict.keys()

        deltas = deltas_dict[neighbors]
        self.width, self.height = image.size

        self.graph = nx.DiGraph()
        self.K = 0

        for cx, cy in product(range(self.width), range(self.height)):
            max_node_flow = 0.0

            for dx, dy in deltas:
                x, y = cx + dx, cy + dy

                if (0 <= x < self.width) and (0 <= y < self.height):
                    weight = boundary_cost(image.getpixel((cx, cy)),
                                           image.getpixel((x, y)),
                                           (cx, cy), (x, y))
                    self.graph.add_edge((cx, cy), (x, y),
                                        capacity=weight)
                    max_node_flow += weight

            self.K = max(self.K, max_node_flow)

        self.K += 1
        self.image = image
        self.lambda_ = lambda_
        self.relative_cost_gen = relative_cost_gen

        self.first_run = True

    def mark(self,
             object_pixels: Iterable[Point] = set(),
             background_pixels: Iterable[Point] = set()):

        def rebuild_graph():
            return self.graph.graph['res_net']

        if object_pixels or background_pixels:
            if self.first_run:
                assert object_pixels and background_pixels

                self.first_run = False

                self.relative_cost = self.relative_cost_gen(self.image,
                                                            object_pixels,
                                                            background_pixels,
                                                            self.K)

                for cx, cy in product(range(self.width), range(self.height)):
                    if (cx, cy) in object_pixels:
                        s_weight = self.K
                        t_weight = 0.0
                    elif (cx, cy) in background_pixels:
                        s_weight = 0.0
                        t_weight = self.K
                    else:
                        s_weight = self.lambda_ * self.relative_cost(
                            (cx, cy), 'background'
                        )
                        t_weight = self.lambda_ * self.relative_cost(
                            (cx, cy), 'object'
                        )

                    self.graph.add_edge('s', (cx, cy), capacity=s_weight)
                    self.graph.add_edge((cx, cy), 't', capacity=t_weight)

                self.graph = get_max_flow(self.graph, 's', 't',
                                          len(self.graph)//10,
                                          value_only=False)
                (s, t) = (self.graph.graph['s_cut'], self.graph.graph['t_cut'])

                self.graph = rebuild_graph()
                return s, t
            else:
                for cx, cy in object_pixels:
                    sp_cap = self.graph['s'][(cx, cy)]['capacity']
                    pt_cap = self.graph[(cx, cy)]['t']['capacity']
                    const = max(sp_cap, pt_cap)
                    self.graph['s'][(cx, cy)]['capacity'] = const + self.K
                    self.graph[(cx, cy)]['t']['capacity'] = const

                for cx, cy in background_pixels:
                    sp_cap = self.graph['s'][(cx, cy)]['capacity']
                    pt_cap = self.graph[(cx, cy)]['t']['capacity']
                    const = max(sp_cap, pt_cap)
                    self.graph['s'][(cx, cy)]['capacity'] = const
                    self.graph[(cx, cy)]['t']['capacity'] = const + self.K

                self.graph = get_max_flow(self.graph, 's', 't',
                                          len(self.graph)//10,
                                          value_only=False)
                (s, t) = (self.graph.graph['s_cut'], self.graph.graph['t_cut'])

                self.graph = rebuild_graph()
                return s, t
