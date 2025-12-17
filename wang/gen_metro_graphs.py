"""
gen_metro_graphs.py

"""

import os
import csv
import math
import random
import zipfile
import argparse
from typing import Dict, List, Tuple


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    """两点球面距离（km）"""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def gen_one_graph(graph_idx: int, rng: random.Random, min_edges: int) -> Tuple[List[dict], List[dict]]:
    """
    生成一份简化地铁图：
    """
    graph_id = f"G{graph_idx:04d}"

    # 线路数与规模：保持“简单”，但确保 edges 很容易 >100
    num_lines = rng.randint(5, 7)
    unique_range = (22, 28)       # 每条线独有站点数（不含换乘站）
    num_transfers = rng.randint(4, 6)

    base_lat = 31.2304 + rng.uniform(-0.15, 0.15)
    base_lon = 121.4737 + rng.uniform(-0.15, 0.15)

    stations: Dict[str, dict] = {}

    # 换乘站在中心附近成环
    transfer_ids: List[str] = []
    for i in range(1, num_transfers + 1):
        sid = f"{graph_id}_T{i:02d}"
        angle = 2 * math.pi * (i - 1) / num_transfers
        lat = base_lat + 0.03 * math.cos(angle) + rng.uniform(-0.004, 0.004)
        lon = base_lon + 0.03 * math.sin(angle) + rng.uniform(-0.004, 0.004)
        stations[sid] = {"station_id": sid, "name": f"{graph_id}-Transfer-{i:02d}", "lat": round(lat, 6), "lon": round(lon, 6)}
        transfer_ids.append(sid)

    # 生成独立站点
    next_num = 1
    def new_station(line_id: str) -> str:
        nonlocal next_num
        sid = f"{graph_id}_{line_id}_S{next_num:03d}"
        next_num += 1
        stations[sid] = {"station_id": sid, "name": f"{graph_id}-{line_id}-Sta-{next_num-1:03d}", "lat": None, "lon": None}
        return sid

    # 每条线路构建站点序列（链），插入 2 个换乘站
    line_sequences: Dict[str, List[str]] = {}
    for li in range(1, num_lines + 1):
        line_id = f"L{li}"
        seq: List[str] = []
        start_t = rng.choice(transfer_ids)
        seq.append(start_t)

        n_unique = rng.randint(*unique_range)
        for _ in range(n_unique):
            seq.append(new_station(line_id))

        mid_t = rng.choice([t for t in transfer_ids if t != start_t])
        end_t = rng.choice([t for t in transfer_ids if t not in (start_t, mid_t)])

        insert_pos = rng.randint(8, min(14, len(seq) - 1))
        seq.insert(insert_pos, mid_t)
        if rng.random() < 0.85:
            seq.append(end_t)

        # 去掉相邻重复
        cleaned = [seq[0]]
        for s in seq[1:]:
            if s != cleaned[-1]:
                cleaned.append(s)
        line_sequences[line_id] = cleaned

    # 坐标分配：每条线沿一个“走廊方向”展开
    coords: Dict[str, Tuple[float, float]] = {t: (stations[t]["lat"], stations[t]["lon"]) for t in transfer_ids}

    for li in range(1, num_lines + 1):
        line_id = f"L{li}"
        seq = line_sequences[line_id]
        anchor = seq[0]
        a_lat, a_lon = coords[anchor]
        ang = rng.uniform(0, 2 * math.pi)
        dx, dy = math.cos(ang), math.sin(ang)
        step = 0.0065 + rng.random() * 0.0025
        for idx, st in enumerate(seq):
            if st in coords:
                continue
            jitter_lat = rng.uniform(-0.0018, 0.0018)
            jitter_lon = rng.uniform(-0.0018, 0.0018)
            coords[st] = (a_lat + step * idx * dx + jitter_lat, a_lon + step * idx * dy + jitter_lon)

    for sid, (lat, lon) in coords.items():
        stations[sid]["lat"] = round(lat, 6)
        stations[sid]["lon"] = round(lon, 6)

    # 建边：线路相邻站点之间
    edges: List[dict] = []
    edge_num = 1
    for li in range(1, num_lines + 1):
        line_id = f"L{li}"
        seq = line_sequences[line_id]
        for a, b in zip(seq[:-1], seq[1:]):
            lat1, lon1 = coords[a]
            lat2, lon2 = coords[b]
            dist = haversine_km(lat1, lon1, lat2, lon2)
            time_min = max(2.0, min(7.0, 1.8 + dist * 2.0 + rng.uniform(-0.6, 0.8)))
            edges.append({
                "edge_id": f"{graph_id}_E{edge_num:04d}",
                "graph_id": graph_id,
                "line_id": line_id,
                "from_station": a,
                "to_station": b,
                "distance_km": round(dist, 3),
                "travel_time_min": round(time_min, 2),
                "bidirectional": 1,
            })
            edge_num += 1

    # 补边：额外连接器（X），直到 edges >= min_edges
    station_ids = list(stations.keys())
    existing = set((e["from_station"], e["to_station"]) for e in edges)
    existing |= set((e["to_station"], e["from_station"]) for e in edges)

    def add_connector(a: str, b: str, line_id: str = "X"):
        nonlocal edge_num
        lat1, lon1 = coords[a]
        lat2, lon2 = coords[b]
        dist = haversine_km(lat1, lon1, lat2, lon2)
        time_min = max(3.0, min(12.0, 2.5 + dist * 1.7 + rng.uniform(-0.7, 1.0)))
        edges.append({
            "edge_id": f"{graph_id}_E{edge_num:04d}",
            "graph_id": graph_id,
            "line_id": line_id,
            "from_station": a,
            "to_station": b,
            "distance_km": round(dist, 3),
            "travel_time_min": round(time_min, 2),
            "bidirectional": 1,
        })
        edge_num += 1
        existing.add((a, b))
        existing.add((b, a))

    # 先加一些换乘站之间的 express 连接
    t_pairs = []
    for i in range(len(transfer_ids)):
        for j in range(i + 1, len(transfer_ids)):
            t_pairs.append((transfer_ids[i], transfer_ids[j]))
    rng.shuffle(t_pairs)
    for a, b in t_pairs[:max(2, len(transfer_ids) - 1)]:
        if (a, b) not in existing:
            add_connector(a, b, "X")

    # 再随机补足，偏向“近距离”连接（更像地铁换乘/支线）
    guard = 0
    while len(edges) < min_edges and guard < 20000:
        guard += 1
        a = rng.choice(station_ids)
        b = rng.choice(station_ids)
        if a == b or (a, b) in existing:
            continue
        lat1, lon1 = coords[a]
        lat2, lon2 = coords[b]
        dist = haversine_km(lat1, lon1, lat2, lon2)
        if dist > 20 and rng.random() < 0.85:
            continue
        add_connector(a, b, "X")

    stations_rows = [{
        "station_id": s["station_id"],
        "graph_id": graph_id,
        "name": s["name"],
        "lat": s["lat"],
        "lon": s["lon"],
    } for s in stations.values()]

    return stations_rows, edges


def write_csv(path: str, fieldnames: List[str], rows: List[dict]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def zip_dir(src_dir: str, zip_path: str):
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(src_dir):
            for fn in files:
                full = os.path.join(root, fn)
                arc = os.path.relpath(full, os.path.dirname(src_dir))
                z.write(full, arcname=arc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--num-graphs", type=int, default=120, help="生成多少份独立地铁图（>=100）")
    ap.add_argument("--min-edges", type=int, default=110, help="每份图至少多少条边（>=100）")
    ap.add_argument("--out-dir", type=str, default="metro_graphs", help="输出目录")
    ap.add_argument("--seed", type=int, default=42, help="随机种子（可复现）")
    ap.add_argument("--zip", action="store_true", help="额外输出一个包含所有CSV的zip")
    args = ap.parse_args()

    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)

    counts = []
    for gi in range(1, args.num_graphs + 1):
        rng = random.Random(args.seed + gi * 10007)  # 每图独立seed
        stations_rows, edges_rows = gen_one_graph(gi, rng, args.min_edges)

        gname = f"graph_{gi:04d}"
        write_csv(
            os.path.join(out_dir, f"{gname}_stations.csv"),
            ["station_id", "graph_id", "name", "lat", "lon"],
            stations_rows
        )
        write_csv(
            os.path.join(out_dir, f"{gname}_edges.csv"),
            ["edge_id", "graph_id", "line_id", "from_station", "to_station", "distance_km", "travel_time_min", "bidirectional"],
            edges_rows
        )

        counts.append((gi, len(stations_rows), len(edges_rows)))

    min_e = min(c[2] for c in counts)
    max_e = max(c[2] for c in counts)
    print(f"Done. graphs={len(counts)} min_edges={min_e} max_edges={max_e}")
    print(f"Output dir: {out_dir}")

    if args.zip:
        zip_path = out_dir.rstrip("/\\") + ".zip"
        zip_dir(out_dir, zip_path)
        print(f"Zipped: {zip_path}")


if __name__ == "__main__":
    main()
