"""
AStarShortestPath.py - A*最短路径算法实现
使用欧几里得距离作为启发式函数的A*算法
"""

from project.Interface import ShortestPathInterface
import heapq
import math
from typing import Dict, List, Tuple, Optional


class AStarShortestPath(ShortestPathInterface):
    """A*算法实现类"""
    
    def __init__(self, coordinates: Optional[Dict[str, Tuple[float, float]]] = None):
        """
        初始化A*算法
        """
        self.coordinates = coordinates or {}
        self.nodes_visited = 0
        self.nodes_expanded = 0
    
    def set_coordinates(self, coordinates: Dict[str, Tuple[float, float]]):
        """设置节点坐标"""
        self.coordinates = coordinates
    
    def compute_shortest_path(
        self,
        graph: Dict[str, List[Tuple[str, float]]],
        start: str,
        end: str,
        landmarks: Optional[List[str]] = None
    ) -> Tuple[float, List[str]]:
        """
        使用 A* 算法计算从 start 到 end 的最短路径
        
        """
        # 重置统计信息
        self.nodes_visited = 0
        self.nodes_expanded = 0
        
        # 初始化
        dist = {node: float('inf') for node in graph}
        dist[start] = 0
        prev = {node: None for node in graph}
        
        # 优先队列：(f值, g值, 节点)
        h_start = self._heuristic(start, end)
        pq = [(h_start, 0, start)]
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
                    
                    # 计算f值 = g值 + h值
                    h_val = self._heuristic(neighbor, end)
                    f_val = new_dist + h_val
                    
                    heapq.heappush(pq, (f_val, new_dist, neighbor))
        
        # 没有找到路径
        return float('inf'), []
    
    def _heuristic(self, node: str, target: str) -> float:
        """
        计算启发式函数 h(node)
        """
        if not self.coordinates or node not in self.coordinates or target not in self.coordinates:
            return 0
        
        lat1, lon1 = self.coordinates[node]
        lat2, lon2 = self.coordinates[target]
        
        return self._haversine_distance(lat1, lon1, lat2, lon2)
    
    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        计算两点间的Haversine距离（球面距离）
        """
        R = 6371.0  # 地球半径（km）
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        
        a = (math.sin(dphi / 2) ** 2 + 
             math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
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
        return "A* (with Haversine heuristic)"
    
    def get_statistics(self) -> Dict[str, int]:
        """返回算法统计信息"""
        return {
            'nodes_visited': self.nodes_visited,
            'nodes_expanded': self.nodes_expanded,
            'has_coordinates': len(self.coordinates) > 0
        }
