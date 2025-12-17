"""
AltShortestPath.py - ALT (A*, Landmarks, Triangle inequality) 算法实现
"""

from project.Interface import ShortestPathInterface
import heapq
from typing import Dict, List, Tuple, Optional


class AltShortestPath(ShortestPathInterface):
    """ALT算法实现类"""
    
    def __init__(self):
        self.nodes_visited = 0
        self.nodes_expanded = 0
        self.landmark_distances = {}
    
    def compute_shortest_path(
        self,
        graph: Dict[str, List[Tuple[str, float]]],
        start: str,
        end: str,
        landmarks: Optional[List[str]] = None
    ) -> Tuple[float, List[str]]:
        """
        使用 ALT 算法计算从 start 到 end 的最短路径
        """
        # 重置统计信息
        self.nodes_visited = 0
        self.nodes_expanded = 0
        
        # 如果没有提供地标，退化为普通Dijkstra
        if not landmarks:
            landmarks = []
        
        # 预计算：从每个地标到所有节点的最短距离
        self.landmark_distances = {}
        for landmark in landmarks:
            self.landmark_distances[landmark] = self._dijkstra_from_landmark(graph, landmark)
        
        # A*搜索
        dist = {node: float('inf') for node in graph}
        dist[start] = 0
        prev = {node: None for node in graph}
        
        # 优先队列：(f值, g值, 节点)，其中f = g + h
        pq = [(0, 0, start)]
        visited = set()
        
        while pq:
            f_val, current_dist, current_node = heapq.heappop(pq)
            
            # 如果已经访问过，跳过
            if current_node in visited:
                continue
            
            visited.add(current_node)
            self.nodes_visited += 1
            
            # 如果到达终点，重建路径
            if current_node == end:
                path = self._reconstruct_path(prev, start, end)
                return current_dist, path
            
            # 扩展邻居节点
            self.nodes_expanded += 1
            for neighbor, weight in graph[current_node]:
                new_dist = current_dist + weight
                
                if new_dist < dist[neighbor]:
                    dist[neighbor] = new_dist
                    prev[neighbor] = current_node
                    
                    # 计算启发式函数h(neighbor)
                    h_val = self._heuristic(neighbor, end, landmarks)
                    f_val = new_dist + h_val
                    
                    heapq.heappush(pq, (f_val, new_dist, neighbor))
        
        # 没有找到路径
        return float('inf'), []
    
    def _dijkstra_from_landmark(
        self,
        graph: Dict[str, List[Tuple[str, float]]],
        landmark: str
    ) -> Dict[str, float]:
        """
        从单个地标节点运行Dijkstra算法，计算到所有节点的最短距离
        """
        dist = {node: float('inf') for node in graph}
        dist[landmark] = 0
        pq = [(0, landmark)]
        
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
    
    def _heuristic(
        self,
        node: str,
        target: str,
        landmarks: List[str]
    ) -> float:
        """
        计算启发式函数 h(node)

        """
        if not landmarks:
            return 0
        
        max_h = 0
        for landmark in landmarks:
            if landmark in self.landmark_distances:
                dist_to_landmark = self.landmark_distances[landmark]
                # 三角不等式下界
                h = abs(dist_to_landmark.get(target, float('inf')) - 
                       dist_to_landmark.get(node, float('inf')))
                max_h = max(max_h, h)
        
        return max_h
    
    def _reconstruct_path(
        self,
        prev: Dict[str, Optional[str]],
        start: str,
        end: str
    ) -> List[str]:
        """
        从前驱字典重建路径
   
        """
        path = []
        current = end
        
        while current is not None:
            path.append(current)
            current = prev[current]
        
        path.reverse()
        
        if path and path[0] == start:
            return path
        else:
            return []
    
    def get_algorithm_name(self) -> str:
        """返回算法名称"""
        return "ALT (A* with Landmarks)"
    
    def get_statistics(self) -> Dict[str, int]:
        """返回算法统计信息"""
        return {
            'nodes_visited': self.nodes_visited,
            'nodes_expanded': self.nodes_expanded,
            'landmarks_used': len(self.landmark_distances)
        }
