from abc import ABC, abstractmethod

class ShortestPathInterface(ABC):
    @abstractmethod
    def compute_shortest_path(self, graph, start, end, landmarks):
        """
        计算从 start 到 end 的最短路径

        :param graph: 图，表示为字典，键是节点，值是邻接表，格式 {node: [(neighbor, weight), ...]}
        :param start: 起始节点
        :param end: 终点节点
        :param landmarks: 地标节点列表，用于 ALT 算法的优化
        :return: 最短路径长度
        """
        pass
