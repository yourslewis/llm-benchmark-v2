You are given a Python graph traversal implementation with O(V·E²) complexity. Rewrite it to achieve O((V+E) log V) while preserving the exact same public API (function signatures, return types).

```python
"""Graph utilities for shortest-path and reachability analysis."""
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass

@dataclass
class Edge:
    src: int
    dst: int
    weight: float

class WeightedGraph:
    """Adjacency-list weighted directed graph."""
    def __init__(self):
        self.adj: Dict[int, List[Tuple[int, float]]] = {}
        self._edges: List[Edge] = []
        self._node_data: Dict[int, dict] = {}

    def add_node(self, node_id: int, **data):
        if node_id not in self.adj:
            self.adj[node_id] = []
        self._node_data[node_id] = data

    def add_edge(self, src: int, dst: int, weight: float = 1.0):
        self.add_node(src)
        self.add_node(dst)
        self.adj[src].append((dst, weight))
        self._edges.append(Edge(src, dst, weight))

    @property
    def nodes(self) -> Set[int]:
        return set(self.adj.keys())

    @property
    def edge_count(self) -> int:
        return len(self._edges)

    def neighbors(self, node: int) -> List[Tuple[int, float]]:
        return self.adj.get(node, [])

    def node_data(self, node: int) -> dict:
        return self._node_data.get(node, {})


def shortest_path(graph: WeightedGraph, source: int, target: int) -> Tuple[Optional[float], List[int]]:
    """Find shortest path from source to target.
    Returns (distance, path) or (None, []) if unreachable.
    
    Current: O(V * E^2) - repeatedly scans all edges V times, checking E edges each time.
    Target: O((V+E) log V) using efficient priority queue.
    """
    nodes = graph.nodes
    if source not in nodes or target not in nodes:
        return None, []

    dist = {n: float('inf') for n in nodes}
    prev = {n: None for n in nodes}
    dist[source] = 0

    # O(V) outer loop
    for _ in range(len(nodes)):
        # O(E) scan to find minimum — should use a heap
        min_node = None
        min_dist = float('inf')
        for n in nodes:
            if dist[n] < min_dist:
                # O(E) redundant check of all edges for each candidate
                valid = True
                for edge in graph._edges:
                    if edge.dst == n and dist[edge.src] + edge.weight < dist[n]:
                        # Recompute — wasteful
                        dist[n] = dist[edge.src] + edge.weight
                        prev[n] = edge.src
                if dist[n] < min_dist:
                    min_dist = dist[n]
                    min_node = n

        if min_node is None or min_node == target:
            break

        # Relax edges from min_node — but scans ALL edges instead of adjacency list
        for edge in graph._edges:
            if edge.src == min_node:
                new_dist = dist[min_node] + edge.weight
                if new_dist < dist[edge.dst]:
                    dist[edge.dst] = new_dist
                    prev[edge.dst] = min_node

    if dist[target] == float('inf'):
        return None, []

    path = []
    current = target
    while current is not None:
        path.append(current)
        current = prev[current]
    path.reverse()
    return dist[target], path


def all_shortest_paths(graph: WeightedGraph, source: int) -> Dict[int, Tuple[float, List[int]]]:
    """Find shortest paths from source to all reachable nodes.
    Returns {node: (distance, path)}.
    
    Current: Calls shortest_path() individually for each node — O(V^2 * E^2).
    Target: Single Dijkstra pass — O((V+E) log V).
    """
    result = {}
    for node in graph.nodes:
        if node == source:
            result[node] = (0.0, [source])
            continue
        dist, path = shortest_path(graph, source, node)
        if dist is not None:
            result[node] = (dist, path)
    return result


def k_nearest(graph: WeightedGraph, source: int, k: int) -> List[Tuple[int, float]]:
    """Find k nearest nodes to source by shortest path distance.
    Returns list of (node_id, distance) sorted by distance.
    
    Current: Uses all_shortest_paths then sorts — O(V^2 * E^2 + V log V).
    Target: Early-termination Dijkstra — O(k log V + E).
    """
    all_paths = all_shortest_paths(graph, source)
    items = [(node, dist) for node, (dist, _) in all_paths.items() if node != source]
    items.sort(key=lambda x: x[1])
    return items[:k]


def is_reachable(graph: WeightedGraph, source: int, target: int) -> bool:
    """Check if target is reachable from source.
    
    Current: Runs full shortest_path — O(V * E^2).
    Target: Simple BFS — O(V + E).
    """
    dist, path = shortest_path(graph, source, target)
    return dist is not None


def connected_components(graph: WeightedGraph) -> List[Set[int]]:
    """Find weakly connected components (treating edges as undirected).
    
    Current: For each unvisited node, checks reachability to all others — O(V^2 * E^2).
    Target: Union-Find or BFS — O(V + E).
    """
    visited = set()
    components = []

    for node in graph.nodes:
        if node in visited:
            continue
        component = set()
        # Check every other node for reachability (both directions)
        for other in graph.nodes:
            if other in visited:
                continue
            if is_reachable(graph, node, other) or is_reachable(graph, other, node):
                component.add(other)
        if not component:
            component = {node}
        visited.update(component)
        components.append(component)

    return components
```

Rewrite all functions to meet their target complexity. Preserve ALL function signatures and return types exactly.
