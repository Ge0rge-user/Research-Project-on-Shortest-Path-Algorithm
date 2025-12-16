"""
PerformanceTest.py - 算法性能测试模块
"""

import time
from typing import Dict, List, Tuple, Any
from project.Interface import ShortestPathInterface


class PerformanceTester:
    """算法性能测试器"""
    
    def __init__(self):
        self.results = []
    
    def test_algorithm(
        self,
        algorithm: ShortestPathInterface,
        graph: Dict[str, List[Tuple[str, float]]],
        start: str,
        end: str,
        landmarks: List[str] = None,
        num_runs: int = 1
    ) -> Dict[str, Any]:
        """
        测试单个算法的性能
        """
        times = []
        path_length = None
        path = None
        stats = None
        
        for _ in range(num_runs):
            start_time = time.perf_counter()
            
            try:
                path_length, path = algorithm.compute_shortest_path(
                    graph, start, end, landmarks
                )
                end_time = time.perf_counter()
                times.append(end_time - start_time)
                
                stats = algorithm.get_statistics()
            
            except Exception as e:
                print(f"Error testing {algorithm.get_algorithm_name()}: {e}")
                return {
                    'algorithm': algorithm.get_algorithm_name(),
                    'error': str(e)
                }
        
        avg_time = sum(times) / len(times) if times else 0
        min_time = min(times) if times else 0
        max_time = max(times) if times else 0
        
        result = {
            'algorithm': algorithm.get_algorithm_name(),
            'path_length': path_length,
            'path': path,
            'path_nodes': len(path) if path else 0,
            'avg_time_ms': round(avg_time * 1000, 4),
            'min_time_ms': round(min_time * 1000, 4),
            'max_time_ms': round(max_time * 1000, 4),
            'num_runs': num_runs,
            'statistics': stats or {}
        }
        
        self.results.append(result)
        return result
    
    def compare_algorithms(
        self,
        algorithms: List[ShortestPathInterface],
        graph: Dict[str, List[Tuple[str, float]]],
        start: str,
        end: str,
        landmarks: List[str] = None,
        num_runs: int = 1
    ) -> List[Dict[str, Any]]:
        """
        比较多个算法的性能
        """
        self.results = []
        
        for algorithm in algorithms:
            result = self.test_algorithm(
                algorithm, graph, start, end, landmarks, num_runs
            )
            
        return self.results
    
    def print_comparison(self):
        """打印性能比较结果"""
        if not self.results:
            print("No results to display.")
            return
        
        print("\n" + "=" * 100)
        print("ALGORITHM PERFORMANCE COMPARISON")
        print("=" * 100)
        
        # 打印表头
        header = f"{'Algorithm':<30} {'Path Length':<15} {'Nodes':<8} {'Avg Time (ms)':<15} {'Visited':<10} {'Expanded':<10}"
        print(header)
        print("-" * 100)
        
        # 打印每个算法的结果
        for result in self.results:
            if 'error' in result:
                print(f"{result['algorithm']:<30} ERROR: {result['error']}")
                continue
            
            algo_name = result['algorithm']
            path_length = f"{result['path_length']:.2f}" if result['path_length'] != float('inf') else "No path"
            path_nodes = result['path_nodes']
            avg_time = f"{result['avg_time_ms']:.4f}"
            
            stats = result.get('statistics', {})
            visited = stats.get('nodes_visited', 'N/A')
            expanded = stats.get('nodes_expanded', 'N/A')
            
            print(f"{algo_name:<30} {path_length:<15} {path_nodes:<8} {avg_time:<15} {visited:<10} {expanded:<10}")
        
        print("=" * 100)
        
        # 找出最快的算法
        valid_results = [r for r in self.results if 'error' not in r and r['path_length'] != float('inf')]
        if valid_results:
            fastest = min(valid_results, key=lambda x: x['avg_time_ms'])
            print(f"\n Fastest Algorithm: {fastest['algorithm']} ({fastest['avg_time_ms']:.4f} ms)")
            
            # 找出访问节点最少的算法
            with_stats = [r for r in valid_results if 'nodes_visited' in r.get('statistics', {})]
            if with_stats:
                most_efficient = min(with_stats, key=lambda x: x['statistics']['nodes_visited'])
                print(f" Most Efficient (fewest nodes visited): {most_efficient['algorithm']} ({most_efficient['statistics']['nodes_visited']} nodes)")
        
        print()
    
    def get_speedup_ratio(self, baseline_algo: str, compare_algo: str) -> float:
        """
        计算相对于基准算法的加速比
        """
        baseline = next((r for r in self.results if r['algorithm'] == baseline_algo), None)
        compare = next((r for r in self.results if r['algorithm'] == compare_algo), None)
        
        if not baseline or not compare or 'error' in baseline or 'error' in compare:
            return 0.0
        
        if compare['avg_time_ms'] == 0:
            return float('inf')
        
        return baseline['avg_time_ms'] / compare['avg_time_ms']
