"""
Visualizer.py - 路径和性能可视化模块

使用matplotlib创建图表和可视化
"""

import matplotlib.pyplot as plt
import matplotlib
from typing import Dict, List, Tuple, Any
import os

# 使用非交互式后端
matplotlib.use('Agg')


class Visualizer:
    """可视化工具类"""
    
    def __init__(self, output_dir: str = "visualizations"):
        """
        初始化可视化器
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 设置中文字体（如果需要）
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    def plot_path_on_map(
        self,
        coordinates: Dict[str, Tuple[float, float]],
        path: List[str],
        title: str = "Shortest Path",
        filename: str = "path_map.png"
    ):
        """
        在地图上绘制路径
        """
        if not path or len(path) < 2:
            print("Path is too short to visualize.")
            return
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # 绘制所有节点（浅色）
        all_lats = [coord[0] for coord in coordinates.values()]
        all_lons = [coord[1] for coord in coordinates.values()]
        ax.scatter(all_lons, all_lats, c='lightgray', s=20, alpha=0.5, zorder=1)
        
        # 绘制路径节点（蓝色）
        path_lats = [coordinates[node][0] for node in path if node in coordinates]
        path_lons = [coordinates[node][1] for node in path if node in coordinates]
        ax.scatter(path_lons, path_lats, c='blue', s=100, alpha=0.7, zorder=3, label='Path nodes')
        
        # 绘制路径连线（红色）
        for i in range(len(path) - 1):
            if path[i] in coordinates and path[i+1] in coordinates:
                lat1, lon1 = coordinates[path[i]]
                lat2, lon2 = coordinates[path[i+1]]
                ax.plot([lon1, lon2], [lat1, lat2], 'r-', linewidth=2, alpha=0.8, zorder=2)
        
        # 标记起点和终点
        start_lat, start_lon = coordinates[path[0]]
        end_lat, end_lon = coordinates[path[-1]]
        ax.scatter([start_lon], [start_lat], c='green', s=300, marker='*', 
                  edgecolors='black', linewidths=2, zorder=4, label='Start')
        ax.scatter([end_lon], [end_lat], c='red', s=300, marker='*', 
                  edgecolors='black', linewidths=2, zorder=4, label='End')
        
        ax.set_xlabel('Longitude', fontsize=12)
        ax.set_ylabel('Latitude', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"Path map saved to: {filepath}")
    
    def plot_performance_comparison(
        self,
        results: List[Dict[str, Any]],
        filename: str = "performance_comparison.png"
    ):
        """
        绘制算法性能比较图
        """
        if not results:
            print("No results to visualize.")
            return
        
        # 过滤掉有错误的结果
        valid_results = [r for r in results if 'error' not in r]
        
        if not valid_results:
            print("No valid results to visualize.")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 提取数据
        algo_names = [r['algorithm'] for r in valid_results]
        avg_times = [r['avg_time_ms'] for r in valid_results]
        nodes_visited = [r['statistics'].get('nodes_visited', 0) for r in valid_results]
        nodes_expanded = [r['statistics'].get('nodes_expanded', 0) for r in valid_results]
        path_lengths = [r['path_length'] if r['path_length'] != float('inf') else 0 
                       for r in valid_results]
        
        # 1. 平均执行时间
        ax1 = axes[0, 0]
        colors = plt.cm.viridis(range(len(algo_names)))
        bars1 = ax1.bar(range(len(algo_names)), avg_times, color=colors, alpha=0.8)
        ax1.set_xticks(range(len(algo_names)))
        ax1.set_xticklabels(algo_names, rotation=15, ha='right', fontsize=9)
        ax1.set_ylabel('Average Time (ms)', fontsize=11)
        ax1.set_title('Execution Time Comparison', fontsize=12, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # 在柱状图上添加数值
        for i, (bar, val) in enumerate(zip(bars1, avg_times)):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(avg_times)*0.01,
                    f'{val:.2f}', ha='center', va='bottom', fontsize=8)
        
        # 2. 访问节点数
        ax2 = axes[0, 1]
        bars2 = ax2.bar(range(len(algo_names)), nodes_visited, color=colors, alpha=0.8)
        ax2.set_xticks(range(len(algo_names)))
        ax2.set_xticklabels(algo_names, rotation=15, ha='right', fontsize=9)
        ax2.set_ylabel('Nodes Visited', fontsize=11)
        ax2.set_title('Nodes Visited Comparison', fontsize=12, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        for i, (bar, val) in enumerate(zip(bars2, nodes_visited)):
            if val > 0:
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(nodes_visited)*0.01,
                        f'{val}', ha='center', va='bottom', fontsize=8)
        
        # 3. 扩展节点数
        ax3 = axes[1, 0]
        bars3 = ax3.bar(range(len(algo_names)), nodes_expanded, color=colors, alpha=0.8)
        ax3.set_xticks(range(len(algo_names)))
        ax3.set_xticklabels(algo_names, rotation=15, ha='right', fontsize=9)
        ax3.set_ylabel('Nodes Expanded', fontsize=11)
        ax3.set_title('Nodes Expanded Comparison', fontsize=12, fontweight='bold')
        ax3.grid(axis='y', alpha=0.3)
        
        for i, (bar, val) in enumerate(zip(bars3, nodes_expanded)):
            if val > 0:
                ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(nodes_expanded)*0.01,
                        f'{val}', ha='center', va='bottom', fontsize=8)
        
        # 4. 路径长度
        ax4 = axes[1, 1]
        bars4 = ax4.bar(range(len(algo_names)), path_lengths, color=colors, alpha=0.8)
        ax4.set_xticks(range(len(algo_names)))
        ax4.set_xticklabels(algo_names, rotation=15, ha='right', fontsize=9)
        ax4.set_ylabel('Path Length', fontsize=11)
        ax4.set_title('Path Length Comparison', fontsize=12, fontweight='bold')
        ax4.grid(axis='y', alpha=0.3)
        
        for i, (bar, val) in enumerate(zip(bars4, path_lengths)):
            if val > 0:
                ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(path_lengths)*0.01,
                        f'{val:.2f}', ha='center', va='bottom', fontsize=8)
        
        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"Performance comparison saved to: {filepath}")
    
    def plot_efficiency_chart(
        self,
        results: List[Dict[str, Any]],
        filename: str = "efficiency_chart.png"
    ):
        """
        绘制效率散点图（时间 vs 访问节点数）
        """
        valid_results = [r for r in results if 'error' not in r and 
                        'nodes_visited' in r['statistics']]
        
        if not valid_results:
            print("No valid results with statistics to visualize.")
            return
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        for result in valid_results:
            algo_name = result['algorithm']
            time_ms = result['avg_time_ms']
            nodes = result['statistics']['nodes_visited']
            
            ax.scatter(nodes, time_ms, s=200, alpha=0.7, label=algo_name)
            ax.annotate(algo_name, (nodes, time_ms), 
                       textcoords="offset points", xytext=(5, 5),
                       fontsize=9, alpha=0.8)
        
        ax.set_xlabel('Nodes Visited', fontsize=12)
        ax.set_ylabel('Average Time (ms)', fontsize=12)
        ax.set_title('Algorithm Efficiency: Time vs Nodes Visited', 
                    fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"Efficiency chart saved to: {filepath}")
