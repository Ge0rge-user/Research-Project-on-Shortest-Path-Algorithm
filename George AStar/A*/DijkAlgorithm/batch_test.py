"""
batch_test.py - 批量测试脚本
在多个地铁图上运行算法并统计平均性能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from project.Dijkstra import DijkstraShortestPath
from project.AStarShortestPath import AStarShortestPath
from project.AltShortestPath import AltShortestPath
from project.DataLoader import MetroDataLoader
from project.PerformanceTest import PerformanceTester
import random


def batch_test(num_graphs: int = 10, num_tests_per_graph: int = 5):
    """
    批量测试多个图

    """
    print("\n" + "="*80)
    print(f"BATCH TEST: {num_graphs} graphs × {num_tests_per_graph} tests each")
    print("="*80)
    
    loader = MetroDataLoader("metro_graphs")
    available_graphs = loader.list_available_graphs()
    
    if not available_graphs:
        print("\n⚠ No metro graphs found. Please run gen_metro_graphs.py first.")
        return
    
    # 随机选择图
    test_graphs = random.sample(
        available_graphs, 
        min(num_graphs, len(available_graphs))
    )
    
    # 累积统计
    total_results = {
        'Dijkstra': {'times': [], 'visited': [], 'expanded': []},
        'A* (with Haversine heuristic)': {'times': [], 'visited': [], 'expanded': []},
        'ALT (A* with Landmarks)': {'times': [], 'visited': [], 'expanded': []}
    }
    
    for i, graph_id in enumerate(test_graphs, 1):
        print(f"\n[{i}/{len(test_graphs)}] Testing {graph_id}...")
        
        try:
            # 加载图
            graph = loader.load_graph(graph_id)
            coordinates = loader.get_coordinates(graph_id)
            
            # 在这个图上进行多次测试
            for j in range(num_tests_per_graph):
                # 随机选择起点、终点和地标
                start, end, landmarks = loader.select_random_nodes(graph, num_landmarks=5)
                
                # 创建算法实例
                dijkstra = DijkstraShortestPath()
                astar = AStarShortestPath(coordinates)
                alt = AltShortestPath()
                
                # 测试每个算法
                for algo in [dijkstra, astar, alt]:
                    tester = PerformanceTester()
                    result = tester.test_algorithm(
                        algorithm=algo,
                        graph=graph,
                        start=start,
                        end=end,
                        landmarks=landmarks,
                        num_runs=1
                    )
                    
                    algo_name = result['algorithm']
                    if algo_name in total_results and 'error' not in result:
                        total_results[algo_name]['times'].append(result['avg_time_ms'])
                        stats = result.get('statistics', {})
                        if 'nodes_visited' in stats:
                            total_results[algo_name]['visited'].append(stats['nodes_visited'])
                        if 'nodes_expanded' in stats:
                            total_results[algo_name]['expanded'].append(stats['nodes_expanded'])
        
        except Exception as e:
            print(f"  Error testing {graph_id}: {e}")
            continue
    
    # 打印汇总统计
    print("\n" + "="*80)
    print("BATCH TEST SUMMARY")
    print("="*80)
    print(f"\nTotal tests: {len(test_graphs)} graphs × {num_tests_per_graph} tests = {len(test_graphs) * num_tests_per_graph} tests\n")
    
    header = f"{'Algorithm':<35} {'Avg Time (ms)':<18} {'Avg Visited':<15} {'Avg Expanded':<15}"
    print(header)
    print("-" * 80)
    
    for algo_name, data in total_results.items():
        if data['times']:
            avg_time = sum(data['times']) / len(data['times'])
            avg_visited = sum(data['visited']) / len(data['visited']) if data['visited'] else 0
            avg_expanded = sum(data['expanded']) / len(data['expanded']) if data['expanded'] else 0
            
            print(f"{algo_name:<35} {avg_time:<18.4f} {avg_visited:<15.1f} {avg_expanded:<15.1f}")
    
    print("="*80)
    
    # 计算改进百分比
    if (total_results['Dijkstra']['times'] and 
        total_results['A* (with Haversine heuristic)']['times']):
        
        dijkstra_avg = sum(total_results['Dijkstra']['times']) / len(total_results['Dijkstra']['times'])
        astar_avg = sum(total_results['A* (with Haversine heuristic)']['times']) / len(total_results['A* (with Haversine heuristic)']['times'])
        
        improvement = ((dijkstra_avg - astar_avg) / dijkstra_avg) * 100
        print(f"\n✓ A* average improvement over Dijkstra: {improvement:.2f}%")
        
        if total_results['ALT (A* with Landmarks)']['times']:
            alt_avg = sum(total_results['ALT (A* with Landmarks)']['times']) / len(total_results['ALT (A* with Landmarks)']['times'])
            alt_improvement = ((dijkstra_avg - alt_avg) / dijkstra_avg) * 100
            print(f"✓ ALT average improvement over Dijkstra: {alt_improvement:.2f}%")
    
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch test shortest path algorithms")
    parser.add_argument('--graphs', type=int, default=10, 
                       help='Number of graphs to test (default: 10)')
    parser.add_argument('--tests', type=int, default=5,
                       help='Number of tests per graph (default: 5)')
    
    args = parser.parse_args()
    
    batch_test(num_graphs=args.graphs, num_tests_per_graph=args.tests)
