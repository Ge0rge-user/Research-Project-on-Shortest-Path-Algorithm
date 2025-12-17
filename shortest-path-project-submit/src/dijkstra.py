# src/dijkstra.py

import heapq

def dijkstra(graph, start):
    """
    Compute shortest paths using Dijkstra's algorithm.

    Args:
      graph: Graph instance (containing adj).
      start: The starting node (must exist in the graph).

    Returns:
      dist: A dictionary {node: distance}.
      prev: A dictionary {node: predecessor}.
    """
    # Initialization
    dist = {node: float("inf") for node in graph.nodes()}
    prev = {node: None for node in graph.nodes()}

    if start not in dist:
        raise ValueError(f"Start node {start} not found in graph")

    dist[start] = 0
    pq = [(0, start)]   # Priority Queue: (distance, node)

    while pq:
        curr_dist, u = heapq.heappop(pq)
        
        # If the popped distance is greater than the known shortest distance, skip it
        if curr_dist > dist[u]:
            continue

        for v, w in graph.neighbors(u):
            if w < 0:
                raise ValueError("Dijkstra does not support negative edge weights")
            
            alt = curr_dist + w
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(pq, (alt, v))

    return dist, prev


def reconstruct_path(prev, target):
    """
    Reconstruct the path from source to target using the prev dictionary.
    Returns a list of nodes. Returns [] if target is unreachable.
    """
    if target not in prev:
        return []
    
    path = []
    cur = target
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    
    path.reverse()
    return path