# src/graph.py

class Graph:
    def __init__(self):
        # Adjacency list: { node: [(neighbor, weight), ...], ... }
        self.adj = {}

    def add_edge(self, u, v, w):
        """Add a directed edge u -> v with weight w."""
        if u not in self.adj:
            self.adj[u] = []
        self.adj[u].append((v, w))
        
        # Ensure v exists in the dictionary (even if it has no outgoing edges)
        # to facilitate distance table initialization.
        if v not in self.adj:
            self.adj[v] = []

    def neighbors(self, u):
        """Return a list of (neighbor, weight) tuples."""
        return self.adj.get(u, [])

    def nodes(self):
        """Return a list of all nodes in the graph."""
        return list(self.adj.keys())

    def load_from_dict(self, data_dict):
        """
        Load graph from a dictionary format: { u: { v: weight, ... }, ... }
        Example: {"A": {"B":4, "C":2}, "B": {"C":5, "D":10}, ...}
        """
        for u, nbrs in data_dict.items():
            for v, w in nbrs.items():
                self.add_edge(u, v, w)