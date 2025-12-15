# src/dijkstra.py

import heapq

def dijkstra(graph, start):
    """
    参数:
      graph: Graph 实例（含 adj）
      start: 起点节点（必须在 graph 中）

    返回:
      dist: {node: distance}
      prev: {node: predecessor}
    """
    # 初始化
    dist = {node: float("inf") for node in graph.nodes()}
    prev = {node: None for node in graph.nodes()}

    if start not in dist:
        raise ValueError(f"start node {start} not in graph")

    dist[start] = 0
    pq = [(0, start)]   # (距离, 节点)

    while pq:
        curr_dist, u = heapq.heappop(pq)
        # 如果弹出的不是最新最短距离，跳过
        if curr_dist > dist[u]:
            continue

        for v, w in graph.neighbors(u):
            if w < 0:
                raise ValueError("Dijkstra 不支持负权边")
            alt = curr_dist + w
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(pq, (alt, v))

    return dist, prev


def reconstruct_path(prev, target):
    """用 prev 字典重建从某个源到 target 的路径（list），如果不可达返回 []"""
    if target not in prev:
        return []
    path = []
    cur = target
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    # 如果最终路径第一项的 predecessor 为空但它不是源，仍可返回（调用端知道起点是谁）
    return path
