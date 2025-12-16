"""
examples.py - 使用示例集合
展示项目各个功能的典型用法
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ============================================================================
# 示例 1: 基础使用 - 简单图测试
# ============================================================================
def example_1_basic_usage():
    """示例1: 在简单图上运行三种算法"""
    print("\n" + "="*60)
    print("Example 1: Basic Usage - Simple Graph")
    print("="*60)
    
    from project import DijkstraShortestPath, AStarShortestPath, AltShortestPath
    
    # 定义简单图
    graph = {
        'A': [('B', 1), ('C', 4)],
        'B': [('A', 1), ('C', 2), ('D', 5)],
        'C': [('A', 4), ('B', 2), ('D', 1)],
        'D': [('B', 5), ('C', 1)]
    }
    
    start, end = 'A', 'D'
    landmarks = ['B', 'C']
    
    # Dijkstra
    dijkstra = DijkstraShortestPath()
    dist, path = dijkstra.compute_shortest_path(graph, start, end)
    print(f"\nDijkstra: {start} → {end}")
    print(f"  Distance: {dist}")
    print(f"  Path: {' → '.join(path)}")
    
    # A*
    astar = AStarShortestPath()
    dist, path = astar.compute_shortest_path(graph, start, end)
    print(f"\nA*: {start} → {end}")
    print(f"  Distance: {dist}")
    print(f"  Path: {' → '.join(path)}")
    
    # ALT
    alt = AltShortestPath()
    dist, path = alt.compute_shortest_path(graph, start, end, landmarks)
    print(f"\nALT: {start} → {end}")
    print(f"  Distance: {dist}")
    print(f"  Path: {' → '.join(path)}")


# ============================================================================
# 示例 2: 数据加载 - 加载地铁网络数据
# ============================================================================
def example_2_load_data():
    """示例2: 从CSV文件加载地铁网络数据"""
    print("\n" + "="*60)
    print("Example 2: Load Metro Network Data")
    print("="*60)
    
    from project import MetroDataLoader
    
    loader = MetroDataLoader("metro_graphs")
    
    # 检查可用图
    available = loader.list_available_graphs()
    if not available:
        print("\n⚠ No metro graphs found.")
        print("Run: python gen_metro_graphs.py --num-graphs 10")
        return None
    
    print(f"\nAvailable graphs: {len(available)}")
    
    # 加载第一个图
    graph_id = available[0]
    print(f"\nLoading: {graph_id}")
    
    graph = loader.load_graph(graph_id)
    coordinates = loader.get_coordinates(graph_id)
    stats = loader.get_graph_statistics(graph)
    
    print(f"Statistics:")
    print(f"  Nodes: {stats['num_nodes']}")
    print(f"  Edges: {stats['num_edges']}")
    print(f"  Avg Degree: {stats['avg_degree']}")
    
    return graph, coordinates, graph_id


# ============================================================================
# 示例 3: 性能测试 - 对比算法性能
# ============================================================================
def example_3_performance_test(graph, coordinates):
    """示例3: 运行性能测试并对比"""
    print("\n" + "="*60)
    print("Example 3: Performance Testing")
    print("="*60)
    
    from project import (
        DijkstraShortestPath,
        AStarShortestPath,
        AltShortestPath,
        MetroDataLoader,
        PerformanceTester
    )
    
    if graph is None:
        print("\n⚠ No graph loaded, skipping performance test")
        return None
    
    # 随机选择节点
    loader = MetroDataLoader()
    start, end, landmarks = loader.select_random_nodes(graph, num_landmarks=5)
    
    print(f"\nTest configuration:")
    print(f"  Start: {start}")
    print(f"  End: {end}")
    print(f"  Landmarks: {len(landmarks)}")
    
    # 创建算法
    dijkstra = DijkstraShortestPath()
    astar = AStarShortestPath(coordinates)
    alt = AltShortestPath()
    
    # 运行测试
    tester = PerformanceTester()
    print("\nRunning tests (10 runs each)...")
    results = tester.compare_algorithms(
        algorithms=[dijkstra, astar, alt],
        graph=graph,
        start=start,
        end=end,
        landmarks=landmarks,
        num_runs=10
    )
    
    # 打印结果
    tester.print_comparison()
    
    return results


# ============================================================================
# 示例 4: 可视化 - 生成图表
# ============================================================================
def example_4_visualization(coordinates, results):
    """示例4: 生成可视化图表"""
    print("\n" + "="*60)
    print("Example 4: Visualization")
    print("="*60)
    
    from project import Visualizer
    
    if not results:
        print("\n⚠ No results to visualize")
        return
    
    visualizer = Visualizer(output_dir="example_visualizations")
    
    # 获取路径
    path = None
    for result in results:
        if 'path' in result and result['path']:
            path = result['path']
            break
    
    if path:
        print("\nGenerating path map...")
        visualizer.plot_path_on_map(
            coordinates=coordinates,
            path=path,
            title="Example: Shortest Path Visualization",
            filename="example_path.png"
        )
    
    print("Generating performance charts...")
    visualizer.plot_performance_comparison(
        results=results,
        filename="example_performance.png"
    )
    
    visualizer.plot_efficiency_chart(
        results=results,
        filename="example_efficiency.png"
    )
    
    print("\n✓ Visualizations saved to 'example_visualizations/'")


# ============================================================================
# 示例 5: 自定义算法 - 扩展A*算法
# ============================================================================
def example_5_custom_algorithm():
    """示例5: 创建自定义算法"""
    print("\n" + "="*60)
    print("Example 5: Custom Algorithm Implementation")
    print("="*60)
    
    from project import AStarShortestPath
    
    class EuclideanAStarShortestPath(AStarShortestPath):
        """使用欧几里得距离的A*算法（适用于平面坐标）"""
        
        def _heuristic(self, node, target):
            """使用简单的欧几里得距离"""
            if not self.coordinates or node not in self.coordinates or target not in self.coordinates:
                return 0
            
            x1, y1 = self.coordinates[node]
            x2, y2 = self.coordinates[target]
            
            return ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        
        def get_algorithm_name(self):
            return "A* (Euclidean)"
    
    # 测试自定义算法
    graph = {
        'A': [('B', 1.4), ('C', 4.0)],
        'B': [('A', 1.4), ('D', 1.4)],
        'C': [('A', 4.0), ('D', 1.4)],
        'D': [('B', 1.4), ('C', 1.4)]
    }
    
    coordinates = {
        'A': (0, 0),
        'B': (1, 1),
        'C': (0, 4),
        'D': (1, 5)
    }
    
    custom_astar = EuclideanAStarShortestPath(coordinates)
    dist, path = custom_astar.compute_shortest_path(graph, 'A', 'D')
    
    print(f"\nCustom A* (Euclidean):")
    print(f"  Distance: {dist}")
    print(f"  Path: {' → '.join(path)}")
    print(f"  Algorithm: {custom_astar.get_algorithm_name()}")


# ============================================================================
# 示例 6: 批量分析 - 多图统计
# ============================================================================
def example_6_batch_analysis():
    """示例6: 批量分析多个图"""
    print("\n" + "="*60)
    print("Example 6: Batch Analysis")
    print("="*60)
    
    from project import MetroDataLoader, DijkstraShortestPath
    import random
    
    loader = MetroDataLoader("metro_graphs")
    available = loader.list_available_graphs()
    
    if len(available) < 3:
        print("\n⚠ Need at least 3 graphs for batch analysis")
        return
    
    # 随机选择3个图
    test_graphs = random.sample(available, 3)
    
    print(f"\nAnalyzing {len(test_graphs)} graphs...")
    
    results_summary = []
    
    for graph_id in test_graphs:
        graph = loader.load_graph(graph_id)
        stats = loader.get_graph_statistics(graph)
        
        # 运行测试
        start, end, _ = loader.select_random_nodes(graph)
        dijkstra = DijkstraShortestPath()
        dist, path = dijkstra.compute_shortest_path(graph, start, end)
        
        results_summary.append({
            'graph_id': graph_id,
            'nodes': stats['num_nodes'],
            'edges': stats['num_edges'],
            'path_length': dist,
            'path_nodes': len(path)
        })
        
        print(f"\n{graph_id}:")
        print(f"  Nodes: {stats['num_nodes']}, Edges: {stats['num_edges']}")
        print(f"  Path: {dist:.2f} ({len(path)} nodes)")
    
    # 汇总统计
    avg_nodes = sum(r['nodes'] for r in results_summary) / len(results_summary)
    avg_path = sum(r['path_length'] for r in results_summary) / len(results_summary)
    
    print(f"\n" + "-"*40)
    print(f"Summary:")
    print(f"  Avg graph size: {avg_nodes:.0f} nodes")
    print(f"  Avg path length: {avg_path:.2f}")


# ============================================================================
# 主函数
# ============================================================================
def main():
    """运行所有示例"""
    print("\n" + "="*60)
    print("SHORTEST PATH ALGORITHMS - USAGE EXAMPLES")
    print("="*60)
    print("\nThis script demonstrates various features of the project.")
    print("Each example is independent and can be run separately.\n")
    
    # 示例1: 基础使用
    example_1_basic_usage()
    
    # 示例2: 数据加载
    result = example_2_load_data()
    if result:
        graph, coordinates, graph_id = result
        
        # 示例3: 性能测试
        results = example_3_performance_test(graph, coordinates)
        
        # 示例4: 可视化
        if results:
            example_4_visualization(coordinates, results)
    
    # 示例5: 自定义算法
    example_5_custom_algorithm()
    
    # 示例6: 批量分析
    example_6_batch_analysis()
    
    print("\n" + "="*60)
    print("ALL EXAMPLES COMPLETED!")
    print("="*60)
    print("\n💡 Tips:")
    print("  - Modify examples.py to test your own scenarios")
    print("  - Check 'example_visualizations/' for generated charts")
    print("  - Refer to README.md for detailed API documentation")
    print()


if __name__ == "__main__":
    main()
