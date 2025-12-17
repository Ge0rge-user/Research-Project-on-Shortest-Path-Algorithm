import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from project.Dijkstra import DijkstraShortestPath
from project.AStarShortestPath import AStarShortestPath
from project.AltShortestPath import AltShortestPath
from project.DataLoader import MetroDataLoader
from project.PerformanceTest import PerformanceTester
from project.Visualizer import Visualizer


def test_simple_graph():
    """测试1: 简单图测试"""
    print("\n" + "="*80)
    print("TEST 1: Simple Graph Test")
    print("="*80)
    
    # 创建简单测试图
    graph = {
        'A': [('B', 1), ('C', 4)],
        'B': [('A', 1), ('C', 2), ('D', 5)],
        'C': [('A', 4), ('B', 2), ('D', 1)],
        'D': [('B', 5), ('C', 1)]
    }
    
    start = 'A'
    end = 'D'
    landmarks = ['B', 'C']
    
    print(f"\nGraph: {len(graph)} nodes")
    print(f"Start: {start}, End: {end}")
    print(f"Landmarks: {landmarks}")
    
    # 测试Dijkstra算法
    print("\n--- Dijkstra Algorithm ---")
    dijkstra = DijkstraShortestPath()
    dist, path = dijkstra.compute_shortest_path(graph, start, end)
    print(f"Shortest path length: {dist}")
    print(f"Path: {' -> '.join(path)}")
    print(f"Statistics: {dijkstra.get_statistics()}")
    
    # 测试A*算法（无坐标，退化为Dijkstra）
    print("\n--- A* Algorithm (without coordinates) ---")
    astar = AStarShortestPath()
    dist, path = astar.compute_shortest_path(graph, start, end)
    print(f"Shortest path length: {dist}")
    print(f"Path: {' -> '.join(path)}")
    print(f"Statistics: {astar.get_statistics()}")
    
    # 测试ALT算法
    print("\n--- ALT Algorithm ---")
    alt = AltShortestPath()
    dist, path = alt.compute_shortest_path(graph, start, end, landmarks)
    print(f"Shortest path length: {dist}")
    print(f"Path: {' -> '.join(path)}")
    print(f"Statistics: {alt.get_statistics()}")


def test_metro_graph():
    """测试2: 地铁网络测试"""
    print("\n" + "="*80)
    print("TEST 2: Metro Network Test")
    print("="*80)
    
    # 加载数据
    loader = MetroDataLoader("metro_graphs")
    
    # 列出可用图
    available_graphs = loader.list_available_graphs()
    
    if not available_graphs:
        print("\n⚠ No metro graphs found. Please run gen_metro_graphs.py first:")
        print("  python gen_metro_graphs.py --num-graphs 120 --min-edges 110")
        return None, None, None, None
    
    print(f"\nFound {len(available_graphs)} metro graphs")
    
    # 选择第一个图进行测试
    graph_id = available_graphs[0]
    print(f"\nLoading graph: {graph_id}")
    
    graph = loader.load_graph(graph_id)
    coordinates = loader.get_coordinates(graph_id)
    
    # 显示图的统计信息
    stats = loader.get_graph_statistics(graph)
    print(f"Graph statistics: {stats}")
    
    # 随机选择起点、终点和地标
    start, end, landmarks = loader.select_random_nodes(graph, num_landmarks=5)
    print(f"\nStart: {start}")
    print(f"End: {end}")
    print(f"Landmarks: {landmarks}")
    
    return graph, coordinates, start, end, landmarks


def performance_comparison(graph, coordinates, start, end, landmarks):
    """测试3: 性能对比"""
    print("\n" + "="*80)
    print("TEST 3: Performance Comparison")
    print("="*80)
    
    # 创建算法实例
    dijkstra = DijkstraShortestPath()
    astar = AStarShortestPath(coordinates)
    alt = AltShortestPath()
    
    algorithms = [dijkstra, astar, alt]
    
    # 创建性能测试器
    tester = PerformanceTester()
    
    # 运行对比测试
    print("\nRunning performance tests (5 runs each)...")
    results = tester.compare_algorithms(
        algorithms=algorithms,
        graph=graph,
        start=start,
        end=end,
        landmarks=landmarks,
        num_runs=5
    )
    
    # 打印对比结果
    tester.print_comparison()
    
    # 计算加速比
    if len(results) >= 2:
        speedup = tester.get_speedup_ratio("Dijkstra", "A* (with Haversine heuristic)")
        if speedup > 0:
            print(f"A* speedup over Dijkstra: {speedup:.2f}x")
        
        speedup_alt = tester.get_speedup_ratio("Dijkstra", "ALT (A* with Landmarks)")
        if speedup_alt > 0:
            print(f"ALT speedup over Dijkstra: {speedup_alt:.2f}x")
    
    return results


def visualize_results(coordinates, path, results):
    """测试4: 可视化"""
    print("\n" + "="*80)
    print("TEST 4: Visualization")
    print("="*80)
    
    visualizer = Visualizer(output_dir="visualizations")
    
    # 绘制路径地图
    print("\nGenerating path visualization...")
    if path and len(path) > 0:
        visualizer.plot_path_on_map(
            coordinates=coordinates,
            path=path,
            title="Shortest Path on Metro Network",
            filename="metro_path.png"
        )
    
    # 绘制性能对比图
    print("Generating performance comparison charts...")
    visualizer.plot_performance_comparison(
        results=results,
        filename="performance_comparison.png"
    )
    
    # 绘制效率图
    print("Generating efficiency chart...")
    visualizer.plot_efficiency_chart(
        results=results,
        filename="efficiency_chart.png"
    )
    
    print("\n All visualizations saved to 'visualizations/' directory.........")


def main():
    """主函数"""
    print("\n" + "="*80)
    print("SHORTEST PATH ALGORITHMS - COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    # 测试1: 简单图
    test_simple_graph()
    
    # 测试2: 地铁网络
    graph, coordinates, start, end, landmarks = test_metro_graph()
    
    if graph is None:
        print("\n⚠ Skipping remaining tests due to missing data")
        return
    
    # 测试3: 性能对比
    results = performance_comparison(graph, coordinates, start, end, landmarks)
    
    # 测试4: 可视化
    # 获取第一个有效结果的路径用于可视化
    path = None
    for result in results:
        if 'path' in result and result['path']:
            path = result['path']
            break
    
    if path:
        visualize_results(coordinates, path, results)
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED..........")
    print("="*80)
    print("\nSummary:")
    print("- Implemented algorithms: Dijkstra, A*, ALT")
    print("- Features: Path reconstruction, performance testing, visualization")
    print("- Check 'visualizations/' directory for output images")
    print()


if __name__ == "__main__":
    main()
