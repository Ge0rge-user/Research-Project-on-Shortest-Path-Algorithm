# -*- coding: utf-8 -*-
"""
generate_one_large_metro.py

每运行一次 -> 随机生成一个“站点很多”的大型地铁网图，并输出：
- JSON：metro_graph.json
- CSV：metro_graph_stations.csv / metro_graph_edges.csv

保证：
- 每次运行随机（不传 seed）
- 图连通
- 站点数 >= min_stations（默认 1000）
- 边数 >= min_edges（默认 3000）
- 无重复无向边

运行：
  python generate_one_large_metro.py
更大：
  python generate_one_large_metro.py --min-stations 1500 --min-edges 5000 --prefix big --out big.json
"""

from __future__ import annotations

import os
import csv
import json
import math
import time
import random
import argparse
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Set


def _rand_id(rng: random.Random, n: int = 10) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(rng.choice(alphabet) for _ in range(n))


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _is_connected(node_ids: List[str], edges: List[dict]) -> bool:
    if not node_ids:
        return False
    g = defaultdict(list)
    for e in edges:
        u, v = e["u"], e["v"]
        g[u].append(v)
        if e.get("bidirectional", True):
            g[v].append(u)
    start = node_ids[0]
    q = deque([start])
    seen = {start}
    while q:
        x = q.popleft()
        for y in g.get(x, []):
            if y not in seen:
                seen.add(y)
                q.append(y)
    return len(seen) == len(node_ids)


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def generate_one_large_metro_graph(
    min_stations: int = 1000,
    min_edges: int = 3000,
    min_lines: int = 14,
    max_lines: int = 22,
    seed: int | None = None,
) -> Dict:
    rng = random.Random(seed if seed is not None else (time.time_ns() % 2**32))

    graph_id = f"metro_{int(time.time())}_{_rand_id(rng, 8)}"
    num_lines = rng.randint(min_lines, max_lines)

    num_hubs = max(8, min(24, int(num_lines * 0.9) + rng.randint(-2, 3)))

    base_lat = 31.2304 + rng.uniform(-0.4, 0.4)
    base_lon = 121.4737 + rng.uniform(-0.4, 0.4)

    nodes: Dict[str, dict] = {}

    # hubs
    hub_ids: List[str] = []
    for i in range(1, num_hubs + 1):
        nid = f"{graph_id}_H{i:03d}"
        ang = 2 * math.pi * (i - 1) / num_hubs
        lat = base_lat + 0.06 * math.cos(ang) + rng.uniform(-0.01, 0.01)
        lon = base_lon + 0.06 * math.sin(ang) + rng.uniform(-0.01, 0.01)
        nodes[nid] = {"id": nid, "name": f"Hub-{i:03d}", "lat": round(lat, 6), "lon": round(lon, 6)}
        hub_ids.append(nid)

    target_unique = max(0, min_stations - len(hub_ids))
    per_line_unique = max(35, int(target_unique / num_lines))
    per_line_unique = rng.randint(int(per_line_unique * 0.85), int(per_line_unique * 1.15))

    next_station_num = 1

    def new_station(line: str) -> str:
        nonlocal next_station_num
        nid = f"{graph_id}_{line}_S{next_station_num:05d}"
        next_station_num += 1
        nodes[nid] = {"id": nid, "name": f"{line}-Sta-{next_station_num-1:05d}", "lat": None, "lon": None}
        return nid

    line_sequences: Dict[str, List[str]] = {}
    coords: Dict[str, Tuple[float, float]] = {hid: (nodes[hid]["lat"], nodes[hid]["lon"]) for hid in hub_ids}

    for li in range(1, num_lines + 1):
        line = f"L{li}"
        k = rng.randint(2, 4)
        hubs = rng.sample(hub_ids, k)
        seq: List[str] = [hubs[0]]

        for segment in range(k - 1):
            n_unique = per_line_unique + rng.randint(-10, 16)
            for _ in range(max(20, n_unique)):
                seq.append(new_station(line))
            seq.append(hubs[segment + 1])

        if rng.random() < 0.7:
            tail = rng.randint(18, 45)
            for _ in range(tail):
                seq.append(new_station(line))

        cleaned = [seq[0]]
        for x in seq[1:]:
            if x != cleaned[-1]:
                cleaned.append(x)
        line_sequences[line] = cleaned

        anchor = cleaned[0]
        a_lat, a_lon = coords[anchor]
        ang = rng.uniform(0, 2 * math.pi)
        step = rng.uniform(0.0038, 0.0075)

        bend_every = rng.randint(18, 35)
        bend = 0.0

        for idx, nid in enumerate(cleaned):
            if nid in coords:
                continue
            if idx % bend_every == 0:
                bend = rng.uniform(-0.8, 0.8)

            ddx = math.cos(ang + bend)
            ddy = math.sin(ang + bend)

            jlat = rng.uniform(-0.0016, 0.0016)
            jlon = rng.uniform(-0.0016, 0.0016)
            coords[nid] = (a_lat + step * idx * ddx + jlat, a_lon + step * idx * ddy + jlon)

    for nid, (lat, lon) in coords.items():
        nodes[nid]["lat"] = round(lat, 6)
        nodes[nid]["lon"] = round(lon, 6)

    # edges
    edges: List[dict] = []
    seen_undirected: Set[Tuple[str, str]] = set()

    def add_edge(u: str, v: str, line: str, w: int = 1):
        a, b = (u, v) if u < v else (v, u)
        if (a, b) in seen_undirected:
            return
        seen_undirected.add((a, b))
        edges.append({"u": u, "v": v, "w": w, "line": line, "bidirectional": True})

    for line, seq in line_sequences.items():
        for u, v in zip(seq[:-1], seq[1:]):
            add_edge(u, v, line, 1)

    # hub ring
    for i in range(len(hub_ids)):
        add_edge(hub_ids[i], hub_ids[(i + 1) % len(hub_ids)], "X", 1)

    node_ids = list(nodes.keys())

    def distance_km(u: str, v: str) -> float:
        lat1, lon1 = coords[u]
        lat2, lon2 = coords[v]
        return _haversine_km(lat1, lon1, lat2, lon2)

    guard = 0
    while len(edges) < min_edges and guard < 200000:
        guard += 1
        u = rng.choice(node_ids)
        v = rng.choice(node_ids)
        if u == v:
            continue
        a, b = (u, v) if u < v else (v, u)
        if (a, b) in seen_undirected:
            continue

        d = distance_km(u, v)
        if d > 18 and rng.random() < 0.90:
            continue
        if d > 30 and rng.random() < 0.98:
            continue

        add_edge(u, v, "X", 1)

    # ensure stations >= min_stations
    while len(nodes) < min_stations:
        line = f"L{rng.randint(1, num_lines)}"
        parent = rng.choice(node_ids)
        nid = new_station(line)
        plat, plon = coords[parent]
        coords[nid] = (plat + rng.uniform(-0.004, 0.004), plon + rng.uniform(-0.004, 0.004))
        nodes[nid]["lat"] = round(coords[nid][0], 6)
        nodes[nid]["lon"] = round(coords[nid][1], 6)
        add_edge(parent, nid, line, 1)
        node_ids.append(nid)

    if not _is_connected(node_ids, edges):
        node_ids_sorted = sorted(node_ids)
        for u, v in zip(node_ids_sorted[:-1], node_ids_sorted[1:]):
            add_edge(u, v, "X", 1)

    # adjacency
    adj: Dict[str, Dict[str, int]] = defaultdict(dict)
    for e in edges:
        u, v, w = e["u"], e["v"], int(e["w"])
        adj[u][v] = min(adj[u].get(v, w), w)
        adj[v][u] = min(adj[v].get(u, w), w)

    return {
        "graph_id": graph_id,
        "generated_at_utc": _utc_now_iso(),
        "nodes": list(nodes.values()),
        "edges": edges,
        "adjacency": adj,
        "stats": {
            "stations": len(nodes),
            "edges": len(edges),
            "lines": num_lines,
            "hubs": num_hubs,
        }
    }


def write_csv(path: str, fieldnames: List[str], rows: List[dict]):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-stations", type=int, default=1000, help="至少多少个站点")
    ap.add_argument("--min-edges", type=int, default=3000, help="至少多少条边")
    ap.add_argument("--out", type=str, default="metro_graph.json", help="输出 JSON 文件名")
    ap.add_argument("--prefix", type=str, default="metro_graph", help="输出 CSV 前缀")
    ap.add_argument("--seed", type=int, default=None, help="固定种子（不填则每次随机）")
    args = ap.parse_args()

    g = generate_one_large_metro_graph(
        min_stations=args.min_stations,
        min_edges=args.min_edges,
        seed=args.seed,
    )

    # JSON
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(g, f, ensure_ascii=False)

    # CSV
    write_csv(
        f"{args.prefix}_stations.csv",
        ["id", "name", "lat", "lon"],
        g["nodes"],
    )
    write_csv(
        f"{args.prefix}_edges.csv",
        ["u", "v", "w", "line", "bidirectional"],
        g["edges"],
    )

    print("OK")
    print("graph_id:", g["graph_id"])
    print("stations:", g["stats"]["stations"], "edges:", g["stats"]["edges"])
    print("JSON :", os.path.abspath(args.out))
    print("CSV  :", os.path.abspath(f"{args.prefix}_stations.csv"))
    print("CSV  :", os.path.abspath(f"{args.prefix}_edges.csv"))


if __name__ == "__main__":
    main()
