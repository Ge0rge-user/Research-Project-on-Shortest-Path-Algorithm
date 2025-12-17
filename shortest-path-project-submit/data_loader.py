# src/data_loader.py

import json
import csv

def load_from_dict_format():
    """
    临时样例数据（项目开始阶段用）
    返回 { u: {v: weight, ...}, ... }
    """
    return {
        "A": {"B": 4, "C": 2},
        "B": {"C": 5, "D": 10},
        "C": {"E": 3},
        "E": {"D": 4},
        "D": {}
    }

def load_from_json(filepath):
    """
    假设 JSON 格式是 { "A": {"B":4, "C":2}, ... }
    D 来时让他给类似格式的 JSON 就能直接 load。
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def load_from_csv(filepath):
    """
    假设 CSV 格式：每行 u,v,weight
    """
    data = {}
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not row or len(row) < 3:
                continue
            u, v, w = row[0].strip(), row[1].strip(), float(row[2])
            if u not in data:
                data[u] = {}
            data[u][v] = w
            # 确保 v 存在（可能没有出边）
            if v not in data:
                data[v] = {}
    return data
