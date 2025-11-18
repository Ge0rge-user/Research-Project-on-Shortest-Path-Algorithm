from project.AltShortestPath import AltShortestPath
from project.Dijkstra import DijkstraShortestPath

def test_shortest_path():
    # 创建图
    graph = {
        'A': [('B', 1), ('C', 4)],
        'B': [('A', 1), ('C', 2), ('D', 5)],
        'C': [('A', 4), ('B', 2), ('D', 1)],
        'D': [('B', 5), ('C', 1)]
    }
    
    # 定义起点、终点和地标节点
    start = 'A'
    end = 'D'
    landmarks = ['B', 'C']
    
    # 使用 ALT 算法
    alt_algorithm = AltShortestPath()
    shortest_path_length = alt_algorithm.compute_shortest_path(graph, start, end, landmarks)
    print(f"使用 ALT 算法计算最短路径从 {start} 到 {end}: {shortest_path_length}")
    
    # 使用 Dijkstra 算法
    dijkstra_algorithm = DijkstraShortestPath()
    shortest_path_length = dijkstra_algorithm.compute_shortest_path(graph, start, end)
    print(f"使用 Dijkstra 算法计算最短路径从 {start} 到 {end}: {shortest_path_length}")

if __name__ == "__main__":
    # 执行测试
    test_shortest_path()
