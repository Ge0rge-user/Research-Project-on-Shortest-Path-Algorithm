"""
Interface.py - 最短路径算法接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional


class ShortestPathInterface(ABC):
    """最短路径算法的抽象基类"""
    
    @abstractmethod
    def compute_shortest_path(
        self,
        graph: Dict[str, List[Tuple[str, float]]],
        start: str,
        end: str,
        landmarks: Optional[List[str]] = None
    ) -> Tuple[float, List[str]]:
        """
        计算从 start 到 end 的最短路径
        """
        pass
    
    @abstractmethod
    def get_algorithm_name(self) -> str:
        """返回算法名称"""
        pass
    
    def get_statistics(self) -> Dict[str, int]:
        """
        返回算法统计信息
        """
        return {
            'nodes_visited': 0,
            'nodes_expanded': 0
        }
