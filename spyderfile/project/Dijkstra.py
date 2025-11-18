from project.Interface import ShortestPathInterface
import heapq

class DijkstraShortestPath(ShortestPathInterface):
    def compute_shortest_path(self, graph, start, end, landmarks=None):
        """
        使用 Dijkstra 算法计算从 start 到 end 的最短路径
        :param graph: 图，表示为字典，键是节点，值是邻接表，格式 {node: [(neighbor, weight), ...]}
        :param start: 起始节点
        :param end: 终点节点
        :param landmarks: 可选参数，用于 Dijkstra 算法的优化，默认为 None
        :return: 最短路径长度
        """
        dist = {node: float('inf') for node in graph}
        dist[start] = 0
        pq = [(0, start)]  # (距离, 节点)
        
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            
            if current_node == end:
                return current_dist
            
            if current_dist > dist[current_node]:
                continue
            
            for neighbor, weight in graph[current_node]:
                distance = current_dist + weight
                if distance < dist[neighbor]:
                    dist[neighbor] = distance
                    heapq.heappush(pq, (distance, neighbor))
        
        return float('inf')  # 如果没有找到路径
