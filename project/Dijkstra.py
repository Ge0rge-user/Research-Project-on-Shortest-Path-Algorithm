"""
Dijkstra.py - Dijkstra最短路径算法实现
"""

from project.Interface import ShortestPathInterface
import heapq
from typing import Dict, List, Tuple, Optional


class DijkstraShortestPath(ShortestPathInterface):
    
    def __init__(self):
        self.nodes_visited = 0
        self.nodes_expanded = 0
    
    def compute_shortest_path(
        self,
        graph: Dict[str, List[Tuple[str, float]]],
        start: str,
        end: str,
        landmarks: Optional[List[str]] = None
    ) -> Tuple[float, List[str]]:
        """
        使用 Dijkstra 算法计算从 start 到 end 的最短路径
        """
        # 重置统计信息
        self.nodes_visited = 0
        self.nodes_expanded = 0
        
        # 初始化距离字典和前驱字典
        dist = {node: float('inf') for node in graph}
        dist[start] = 0
        prev = {node: None for node in graph}
        
        # 优先队列：(距离, 节点)
        pq = [(0, start)]
        visited = set()
        
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            
            # 如果已经访问过，跳过
            if current_node in visited:
                continue
            
            visited.add(current_node)
            self.nodes_visited += 1
            
            # 如果到达终点，重建路径
            if current_node == end:
                path = self._reconstruct_path(prev, start, end)
                return current_dist, path
            
            # 如果当前距离大于已知距离，跳过
            if current_dist > dist[current_node]:
                continue
            
            # 扩展邻居节点
            self.nodes_expanded += 1
            for neighbor, weight in graph[current_node]:
                distance = current_dist + weight
                
                if distance < dist[neighbor]:
                    dist[neighbor] = distance
                    prev[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))
        
        # 没有找到路径
        return float('inf'), []
    
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
        
        # 验证路径是否从start开始
        if path and path[0] == start:
            return path
        else:
            return []
    
    def get_algorithm_name(self) -> str:
        """返回算法名称"""
        return "Dijkstra"
    
    def get_statistics(self) -> Dict[str, int]:
        """返回算法统计信息"""
        return {
            'nodes_visited': self.nodes_visited,
            'nodes_expanded': self.nodes_expanded
        }
