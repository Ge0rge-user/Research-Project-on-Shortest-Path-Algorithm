# src/graph.py

class Graph:
    def __init__(self):
        # 邻接表：{ node: [(neighbor, weight), ...], ... }
        self.adj = {}

    def add_edge(self, u, v, w):
        """添加有向边 u -> v 权重 w"""
        if u not in self.adj:
            self.adj[u] = []
        self.adj[u].append((v, w))
        # 确保 v 在字典中（即使没有出边），方便初始化距离表
        if v not in self.adj:
            self.adj[v] = []

    def neighbors(self, u):
        """返回 (v, w) 列表"""
        return self.adj.get(u, [])

    def nodes(self):
        """返回所有节点的列表"""
        return list(self.adj.keys())

    def load_from_dict(self, data_dict):
        """
        读取格式： { u: { v: weight, ... }, ... }
        例如 {"A": {"B":4, "C":2}, "B": {"C":5, "D":10}, ...}
        """
        for u, nbrs in data_dict.items():
            for v, w in nbrs.items():
                self.add_edge(u, v, w)
