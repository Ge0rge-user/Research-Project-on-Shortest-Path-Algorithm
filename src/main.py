# src/main.py
from graph import Graph
from dijkstra import dijkstra, reconstruct_path
from data_loader import load_from_dict_format, load_from_json, load_from_csv, load_metro_adjacency
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
    print("Shortest distance table:")
    for node, d in sorted(dist.items()):
        print(f"{start} -> {node}: {d if d != float('inf') else 'inf'}")
    target = "D"
    path = reconstruct_path(prev, target)
    print("\nExample path (A -> D):", " -> ".join(path) if path else "No path")

if __name__ == "__main__":
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
        elif fmt == "metro":  # Support metro adjacency.json
            data = load_metro_adjacency(filepath)
        else:
            print("Error: Format must be 'json', 'csv' or 'metro'")
            sys.exit(1)

        g = build_graph_from_data(data)
        dist, prev = dijkstra(g, start)

        print(f"Shortest distances (in transfers) from {start} to all stations:")
        for node, d in sorted(dist.items()):
            if d != float('inf'):
                print(f"{start} -> {node}: {d}")
            else:
                print(f"{start} -> {node}: inf (unreachable)")

        if target:
            path = reconstruct_path(prev, target)
            if path and len(path) > 1:
                print(f"\nShortest path ({start} -> {target}), {len(path)-1} transfers ({len(path)} stations):")
                print(" -> ".join(path))
            else:
                print(f"\nNo path from {start} to {target}")