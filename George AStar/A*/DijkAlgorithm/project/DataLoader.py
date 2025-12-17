"""
DataLoader.py - 地铁图数据加载器
"""

import csv
import os
from typing import Dict, List, Tuple, Optional
import random


class MetroDataLoader:
    """地铁网络数据加载器"""
    
    def __init__(self, data_dir: str = "metro_graphs"):
        """
        初始化数据加载器
        """
        self.data_dir = data_dir
        self.graphs_data = {}
        self.coordinates = {}
    
    def load_graph(self, graph_id: str) -> Dict[str, List[Tuple[str, float]]]:
        """
        加载指定的地铁图
        """
        stations_file = os.path.join(self.data_dir, f"{graph_id}_stations.csv")
        edges_file = os.path.join(self.data_dir, f"{graph_id}_edges.csv")
        
        # 检查文件是否存在
        if not os.path.exists(stations_file) or not os.path.exists(edges_file):
            raise FileNotFoundError(f"Graph files not found for {graph_id}")
        
        # 加载站点信息
        stations = self._load_stations(stations_file)
        
        # 加载边信息并构建图
        graph = self._load_edges(edges_file, stations)
        
        # 保存坐标信息
        self.coordinates[graph_id] = {
            sid: (s['lat'], s['lon']) for sid, s in stations.items()
        }
        
        return graph
    
    def _load_stations(self, filepath: str) -> Dict[str, dict]:
        """
        加载站点CSV文件
        """
        stations = {}
        
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                station_id = row['station_id']
                stations[station_id] = {
                    'station_id': station_id,
                    'graph_id': row['graph_id'],
                    'name': row['name'],
                    'lat': float(row['lat']),
                    'lon': float(row['lon'])
                }
        
        return stations
    
    def _load_edges(
        self,
        filepath: str,
        stations: Dict[str, dict]
    ) -> Dict[str, List[Tuple[str, float]]]:
        """
        加载边CSV文件并构建邻接表
        """
        # 初始化邻接表
        graph = {sid: [] for sid in stations}
        
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                from_station = row['from_station']
                to_station = row['to_station']
                
                # 使用travel_time_min作为权重
                weight = float(row['travel_time_min'])
                
                # 添加边
                graph[from_station].append((to_station, weight))
                
                # 如果是双向边，添加反向边
                if int(row.get('bidirectional', 1)) == 1:
                    graph[to_station].append((from_station, weight))
        
        return graph
    
    def get_coordinates(self, graph_id: str) -> Dict[str, Tuple[float, float]]:
        """
        获取指定图的节点坐标
        """
        if graph_id not in self.coordinates:
            self.load_graph(graph_id)
        
        return self.coordinates[graph_id]
    
    def list_available_graphs(self) -> List[str]:
        """
        列出所有可用的图ID
        """
        if not os.path.exists(self.data_dir):
            return []
        
        graphs = set()
        for filename in os.listdir(self.data_dir):
            if filename.endswith('_stations.csv'):
                graph_id = filename.replace('_stations.csv', '')
                graphs.add(graph_id)
        
        return sorted(list(graphs))
    
    def select_random_nodes(
        self,
        graph: Dict[str, List[Tuple[str, float]]],
        num_landmarks: int = 3
    ) -> Tuple[str, str, List[str]]:
        """
        从图中随机选择起点、终点和地标节点
        """
        nodes = list(graph.keys())
        
        if len(nodes) < num_landmarks + 2:
            num_landmarks = max(0, len(nodes) - 2)
        
        selected = random.sample(nodes, num_landmarks + 2)
        start = selected[0]
        end = selected[1]
        landmarks = selected[2:]
        
        return start, end, landmarks
    
    def get_graph_statistics(
        self,
        graph: Dict[str, List[Tuple[str, float]]]
    ) -> Dict[str, int]:
        """
        获取图的统计信息
        """
        num_nodes = len(graph)
        num_edges = sum(len(neighbors) for neighbors in graph.values()) // 2
        
        return {
            'num_nodes': num_nodes,
            'num_edges': num_edges,
            'avg_degree': round(num_edges * 2 / num_nodes, 2) if num_nodes > 0 else 0
        }
