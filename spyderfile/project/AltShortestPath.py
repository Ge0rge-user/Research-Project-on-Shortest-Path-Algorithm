from project.Interface import ShortestPathInterface
import heapq

class AltShortestPath(ShortestPathInterface):
    def dijkstra(self, graph, start):
        """
        计算从 start 节点到所有节点的最短路径
        :param graph: 图，表示为字典，键是节点，值是邻接表，格式 {node: [(neighbor, weight), ...]}
        :param start: 起始节点
        :return: dist 字典，记录从 start 到其他节点的最短距离
        """
        dist = {node: float('inf') for node in graph}
        dist[start] = 0
        pq = [(0, start)]  # (距离, 节点)
        
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            
            if current_dist > dist[current_node]:
                continue
            
            for neighbor, weight in graph[current_node]:
                distance = current_dist + weight
                if distance < dist[neighbor]:
                    dist[neighbor] = distance
                    heapq.heappush(pq, (distance, neighbor))
        
        return dist

    def compute_shortest_path(self, graph, start, end, landmarks):
        """
        使用 ALT 算法计算从 start 到 end 的最短路径
        :param graph: 图，表示为字典，键是节点，值是邻接表，格式 {node: [(neighbor, weight), ...]}
        :param start: 起始节点
        :param end: 终点节点
        :param landmarks: 地标节点列表
        :return: 最短路径长度
        """
        # 1. 计算从所有地标到所有节点的最短路径
        landmark_distances = {}
        for landmark in landmarks:
            landmark_distances[landmark] = self.dijkstra(graph, landmark)
        
        # 2. 计算从 start 到 end 的 A* 算法
        dist_start = {node: float('inf') for node in graph}
        dist_start[start] = 0
        pq = [(0, start)]  # (估算距离, 节点)
        
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            
            if current_node == end:
                return current_dist
            
            if current_dist > dist_start[current_node]:
                continue
            
            for neighbor, weight in graph[current_node]:
                # 计算启发式函数，估算从 neighbor 到 end 的距离
                min_heuristic = float('inf')
                for landmark in landmarks:
                    heuristic = landmark_distances[landmark][current_node] + landmark_distances[landmark][end]
                    min_heuristic = min(min_heuristic, heuristic)
                
                # A* 更新
                new_dist = current_dist + weight + min_heuristic
                if new_dist < dist_start[neighbor]:
                    dist_start[neighbor] = new_dist
