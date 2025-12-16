import time
import heapq
import random
import math
from typing import Dict, List, Tuple, Optional

print("=" * 80)
print("Algorithm Comparison Test")
print("=" * 80)

class Graph:
    def __init__(self, directed: bool = True):
        self.directed = directed
        self.adj: Dict = {}

    def add_edge(self, u, v, w) -> None:
        if u not in self.adj:
            self.adj[u] = []
        if v not in self.adj:
            self.adj[v] = []
        self.adj[u].append((v, w))
        if not self.directed:
            self.adj[v].append((u, w))

    def neighbors(self, u) -> List:
        return self.adj.get(u, [])

    def nodes(self) -> List:
        return list(self.adj.keys())


def euclidean(a, b) -> float:
    (x1, y1), (x2, y2) = a, b
    return math.hypot(x1 - x2, y1 - y2)


def bellman_ford_colab(graph, source):
    nodes = graph.nodes()
    dist = {v: math.inf for v in nodes}
    pred = {v: None for v in nodes}
    dist[source] = 0.0
    relax_count = 0

    for _ in range(len(nodes) - 1):
        updated = False
        for u in nodes:
            for v, w in graph.neighbors(u):
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    pred[v] = u
                    relax_count += 1
                    updated = True
        if not updated:
            break

    return dist, pred, relax_count


def astar_colab(graph, start, goal, heuristic):
    open_heap = []
    heapq.heappush(open_heap, (0.0, start))
    g = {start: 0.0}
    came_from = {}
    closed = set()
    expanded_nodes = 0

    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current in closed:
            continue

        closed.add(current)
        expanded_nodes += 1

        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path, g[path[-1]], expanded_nodes

        for neighbor, weight in graph.neighbors(current):
            tentative_g = g[current] + weight
            if tentative_g < g.get(neighbor, math.inf):
                g[neighbor] = tentative_g
                came_from[neighbor] = current
                f = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_heap, (f, neighbor))

    return None, math.inf, expanded_nodes


def dijkstra_optimized(graph, start, goal):
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    prev = {node: None for node in graph}
    pq = [(0, start)]
    visited = set()
    nodes_visited = 0

    while pq:
        current_dist, current = heapq.heappop(pq)
        
        if current in visited:
            continue
        
        visited.add(current)
        nodes_visited += 1
        
        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = prev[current]
            return dist[goal], path[::-1], nodes_visited
        
        if current_dist > dist[current]:
            continue
        
        for neighbor, weight in graph[current]:
            distance = current_dist + weight
            if distance < dist[neighbor]:
                dist[neighbor] = distance
                prev[neighbor] = current
                heapq.heappush(pq, (distance, neighbor))
    
    return float('inf'), [], nodes_visited


def astar_optimized(graph, start, goal, coordinates):
    def heuristic(node1, node2):
        x1, y1 = coordinates[node1]
        x2, y2 = coordinates[node2]
        return math.hypot(x1 - x2, y1 - y2)
    
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    prev = {node: None for node in graph}
    pq = [(heuristic(start, goal), 0, start)]
    visited = set()
    nodes_visited = 0

    while pq:
        _, current_dist, current = heapq.heappop(pq)
        
        if current in visited:
            continue
        
        visited.add(current)
        nodes_visited += 1
        
        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = prev[current]
            return dist[goal], path[::-1], nodes_visited
        
        for neighbor, weight in graph[current]:
            new_dist = current_dist + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = current
                f = new_dist + heuristic(neighbor, goal)
                heapq.heappush(pq, (f, new_dist, neighbor))
    
    return float('inf'), [], nodes_visited


def generate_test_graph(size=30):
    random.seed(42)
    colab_graph = Graph(directed=False)
    opt_graph = {}
    coordinates = {}
    
    for x in range(size):
        for y in range(size):
            node = (x, y)
            coordinates[node] = (float(x), float(y))
            opt_graph[node] = []
            
            for dx, dy in [(1, 0), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < size and 0 <= ny < size:
                    neighbor = (nx, ny)
                    weight = random.randint(1, 5)
                    
                    colab_graph.add_edge(node, neighbor, float(weight))
                    opt_graph[node].append((neighbor, float(weight)))
                    
                    if neighbor not in opt_graph:
                        opt_graph[neighbor] = []
                    opt_graph[neighbor].append((node, float(weight)))
    
    return colab_graph, opt_graph, coordinates


print("\nGenerating test data (30×30 grid)...")
colab_graph, opt_graph, coordinates = generate_test_graph(size=30)

start = (0, 0)
goal = (29, 29)

print(f"Start: {start}")
print(f"Goal: {goal}")
print(f"Nodes: {len(opt_graph)}")

results = []

print("\n" + "=" * 80)
print("Running tests...")
print("=" * 80)

print("\n[1/4] Bellman-Ford (Your code)...")
t1 = time.perf_counter()
dist, pred, relax_count = bellman_ford_colab(colab_graph, start)
t2 = time.perf_counter()
bf_time = (t2 - t1) * 1000

path = [goal]
current = goal
while pred[current] is not None:
    current = pred[current]
    path.append(current)
path.reverse()

print(f"  Time: {bf_time:.3f} ms")
print(f"  Path cost: {dist[goal]:.1f}")
print(f"  Relaxations: {relax_count}")

results.append(("Bellman-Ford", bf_time, dist[goal], relax_count))

print("\n[2/4] A* (Your code)...")
t1 = time.perf_counter()
path_c, cost_c, expanded_c = astar_colab(colab_graph, start, goal, euclidean)
t2 = time.perf_counter()
astar_c_time = (t2 - t1) * 1000

print(f"  Time: {astar_c_time:.3f} ms")
print(f"  Path cost: {cost_c:.1f}")
print(f"  Nodes visited: {expanded_c}")

results.append(("A* (Colab)", astar_c_time, cost_c, expanded_c))

print("\n[3/4] Dijkstra (Optimized)...")
t1 = time.perf_counter()
cost_d, path_d, visited_d = dijkstra_optimized(opt_graph, start, goal)
t2 = time.perf_counter()
dijkstra_time = (t2 - t1) * 1000

print(f"  Time: {dijkstra_time:.3f} ms")
print(f"  Path cost: {cost_d:.1f}")
print(f"  Nodes visited: {visited_d}")

results.append(("Dijkstra (Optimized)", dijkstra_time, cost_d, visited_d))

print("\n[4/4] A* (Optimized)...")
t1 = time.perf_counter()
cost_a, path_a, visited_a = astar_optimized(opt_graph, start, goal, coordinates)
t2 = time.perf_counter()
astar_o_time = (t2 - t1) * 1000

print(f"  Time: {astar_o_time:.3f} ms")
print(f"  Path cost: {cost_a:.1f}")
print(f"  Nodes visited: {visited_a}")

results.append(("A* (Optimized)", astar_o_time, cost_a, visited_a))

print("\n" + "=" * 80)
print("Comparison Results")
print("=" * 80)

print(f"\n{'Algorithm':<25} {'Time(ms)':<12} {'Path Cost':<12} {'Operations':<12} {'Speedup':<10}")
print("-" * 80)

baseline = results[0][1]

for name, time_ms, cost, ops in results:
    speedup = baseline / time_ms
    print(f"{name:<25} {time_ms:<12.3f} {cost:<12.1f} {ops:<12} {speedup:.2f}x")

print("=" * 80)

fastest = min(results, key=lambda x: x[1])
print(f"\nFastest: {fastest[0]} ({fastest[1]:.3f} ms)")

colab_best = results[1][1]
opt_best = results[3][1]

if opt_best < colab_best:
    improvement = (colab_best - opt_best) / colab_best * 100
    print(f"Optimized version is {improvement:.1f}% faster")
else:
    print(f"Colab version performed better in this test")

print("\n" + "=" * 80)
print("Test completed!")
print("=" * 80)