# src/main.py

from graph import Graph
from dijkstra import dijkstra, reconstruct_path
from data_loader import load_from_dict_format, load_from_json, load_from_csv
import sys

def build_graph_from_data(data_dict):
    g = Graph()
    g.load_from_dict(data_dict)
    return g

def demo_with_temp_data():
    data = load_from_dict_format()
    g = build_graph_from_data(data)
    start = "A"
    dist, prev = dijkstra(g, start)

    print("最短距离表：")
    for node, d in dist.items():
        print(f"{start} -> {node}: {d}")

    target = "D"
    path = reconstruct_path(prev, target)
    print("\n示例路径 (A -> D):", " -> ".join(path))


if __name__ == "__main__":
    # usage: python main.py [json|csv] [path_to_file] start_node target_node
    if len(sys.argv) == 1:
        demo_with_temp_data()
    else:
        fmt = sys.argv[1].lower()
        filepath = sys.argv[2]
        start = sys.argv[3]
        target = sys.argv[4] if len(sys.argv) > 4 else None

        if fmt == "json":
            data = load_from_json(filepath)
        elif fmt == "csv":
            data = load_from_csv(filepath)
        else:
            print("format must be json or csv")
            sys.exit(1)

        g = build_graph_from_data(data)
        dist, prev = dijkstra(g, start)
        print("最短距离：")
        for node, d in dist.items():
            print(f"{start} -> {node}: {d}")
        if target:
            print("\n路径：", " -> ".join(reconstruct_path(prev, target)))
