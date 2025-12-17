# -*- coding: utf-8 -*-
import csv
import json
import re
from collections import defaultdict
from typing import Dict, List

# =======================
# 原始 CTA 数据（来自你上传的文件，原样保留）
# =======================
cta_data = [
    ["Line Name","Line Color","Station Name"],
    ["Red Line","red","Howard"],
    ["Red Line","red","Jarvis"],
    ["Red Line","red","Morse"],
    ["Red Line","red","Loyola"],
    ["Red Line","red","Granville"],
    ["Red Line","red","Thorndale"],
    ["Red Line","red","Bryn Mawr"],
    ["Red Line","red","Berwyn"],
    ["Red Line","red","Argyle"],
    ["Red Line","red","Lawrence"],
    ["Red Line","red","Wilson"],
    ["Red Line","red","Sheridan"],
    ["Red Line","red","Addison"],
    ["Red Line","red","Belmont"],
    ["Red Line","red","Fullerton"],
    ["Red Line","red","North/Clybourn"],
    ["Red Line","red","Clark/Division"],
    ["Red Line","red","Chicago"],
    ["Red Line","red","Grand"],
    ["Red Line","red","Lake"],
    ["Red Line","red","Monroe"],
    ["Red Line","red","Jackson"],
    ["Red Line","red","Harrison"],
    ["Red Line","red","Roosevelt"],
    ["Red Line","red","Cermak-Chinatown"],
    ["Red Line","red","Sox-35th"],
    ["Red Line","red","47th"],
    ["Red Line","red","Garfield"],
    ["Red Line","red","63rd"],
    ["Red Line","red","69th"],
    ["Red Line","red","79th"],
    ["Red Line","red","87th"],
    ["Red Line","red","95th/Dan Ryan"],

    ["Blue Line","blue","O'Hare"],
    ["Blue Line","blue","Rosemont"],
    ["Blue Line","blue","Cumberland"],
    ["Blue Line","blue","Harlem"],
    ["Blue Line","blue","Jefferson Park"],
    ["Blue Line","blue","Montrose"],
    ["Blue Line","blue","Irving Park"],
    ["Blue Line","blue","Addison"],
    ["Blue Line","blue","Belmont"],
    ["Blue Line","blue","Logan Square"],
    ["Blue Line","blue","California"],
    ["Blue Line","blue","Western"],
    ["Blue Line","blue","Damen"],
    ["Blue Line","blue","Division"],
    ["Blue Line","blue","Chicago"],
    ["Blue Line","blue","Grand"],
    ["Blue Line","blue","Clark/Lake"],
    ["Blue Line","blue","Washington"],
    ["Blue Line","blue","Monroe"],
    ["Blue Line","blue","Jackson"],
    ["Blue Line","blue","LaSalle"],
    ["Blue Line","blue","Clinton"],
    ["Blue Line","blue","UIC-Halsted"],
    ["Blue Line","blue","Racine"],
    ["Blue Line","blue","Illinois Medical District"],
    ["Blue Line","blue","Western"],
    ["Blue Line","blue","Kedzie-Homan"],
    ["Blue Line","blue","Pulaski"],
    ["Blue Line","blue","Cicero"],
    ["Blue Line","blue","Austin"],
    ["Blue Line","blue","Oak Park"],
    ["Blue Line","blue","Forest Park"],
]
# =======================


BAD_STATIONS = {
    "Unknown Station",
    "Selected Stations",
    "Temporarily Closed Station",
}

def slug_station(name: str) -> str:
    s = name.strip().lower()
    s = s.replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return f"st_{s}"

def build_graph(cta_data: List[List[str]]):
    rows = cta_data[1:]

    line_seq = defaultdict(list)
    station_info = {}

    for r in rows:
        line_name = r[0].strip()
        station_name = r[2].strip()
        if not station_name or station_name in BAD_STATIONS:
            continue

        sid = slug_station(station_name)

        if sid not in station_info:
            station_info[sid] = {
                "station_id": sid,
                "station_name": station_name,
                "lines": set(),
            }
        station_info[sid]["lines"].add(line_name)

        if not line_seq[line_name] or line_seq[line_name][-1] != sid:
            line_seq[line_name].append(sid)

    edges = []
    for line, seq in line_seq.items():
        for a, b in zip(seq[:-1], seq[1:]):
            edges.append({
                "from_station_id": a,
                "to_station_id": b,
                "line_name": line,
                "weight": 1,
                "bidirectional": 1
            })

    adj = defaultdict(dict)
    for e in edges:
        a, b = e["from_station_id"], e["to_station_id"]
        adj[a][b] = 1
        adj[b][a] = 1

    stations = []
    for s in station_info.values():
        stations.append({
            "station_id": s["station_id"],
            "station_name": s["station_name"],
            "lines": "|".join(sorted(s["lines"]))
        })

    return stations, edges, dict(adj)

def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

if __name__ == "__main__":
    stations, edges, adj = build_graph(cta_data)

    write_csv("chicago_cta_stations.csv", stations,
              ["station_id","station_name","lines"])
    write_csv("chicago_cta_edges.csv", edges,
              ["from_station_id","to_station_id","line_name","weight","bidirectional"])

    with open("chicago_cta_adjacency.json","w",encoding="utf-8") as f:
        json.dump(adj,f,ensure_ascii=False)

    print(f"OK: stations={len(stations)}, edges={len(edges)}")
