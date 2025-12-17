# -*- coding: utf-8 -*-
"""
nyc_subway_graph_export.py

做同样的事：在不改变你原始 nyc_subway_data 的前提下，
把它转换成“图数据”并输出 CSV/JSON，满足最短路算法输入。

输入：
- nyc_subway_data（你原文件里的表格数据，已原样粘贴）

输出（运行后在当前目录生成）：
- nyc_subway_stations.csv      (station_id, station_name, lines, boroughs, station_status, transfer_station, accessible, remarks)
- nyc_subway_edges.csv         (from_station_id, to_station_id, line_name, weight, bidirectional)
- nyc_subway_adjacency.json    (邻接表)

规则（最小必要改动）：
- station_id 由站名生成（同名站自动合并为换乘站）
- 按每条 Line 的出现顺序连相邻站为边（weight=1）
- 过滤明显不是“具体站点”的集合/占位项（如 'The Bronx Stations'、'Staten Island Stations'）
"""

import csv

nyc_subway_data = [
    ['Line Name', 'Line Color', 'Station Name', 'Borough', 'Station Status', 'Transfer Station', 'Accessible', 'Remarks'],
    # 1 Line (Red)
    ['1 Line', 'Red', 'Van Cortlandt Park-242 St', 'The Bronx', 'In Service', 'Yes', 'Yes', 'Metro-North interchange'],
    ['1 Line', 'Red', '238 St', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', '233 St', 'The Bronx', 'In Service', 'Yes', 'Yes', 'Metro-North interchange'],
    ['1 Line', 'Red', '225 St', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', '215 St', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', '207 St', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', '191 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', '181 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', '168 St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to A/C Lines'],
    ['1 Line', 'Red', '157 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', '145 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', '137 St-City College', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', '125 St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 2/3/A/B/C/D Lines'],
    ['1 Line', 'Red', '116 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', '110 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', '103 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', '96 St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 2/3 Lines'],
    ['1 Line', 'Red', '86 St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 2/3 Lines'],
    ['1 Line', 'Red', '79 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', '72 St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 2/3 Lines'],
    ['1 Line', 'Red', '66 St-Lincoln Center', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', '59 St-Columbus Circle', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to A/B/C/D Lines'],
    ['1 Line', 'Red', '50 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', '42 St-Port Authority Bus Terminal', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to A/C/E/2/3/N/Q/R/W Lines'],
    ['1 Line', 'Red', '34 St-Penn Station', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Amtrak/LIRR interchange'],
    ['1 Line', 'Red', '28 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', '23 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', '18 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', '14 St-Union Square', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 2/3/N/Q/R/W/L Lines'],
    ['1 Line', 'Red', '8 St-NYU', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', 'Christopher St-Sheridan Square', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', 'Houston St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', 'Canal St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to A/C/E/N/Q/R/W Lines'],
    ['1 Line', 'Red', 'Chambers St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', 'Franklin St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', 'Rector St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', 'Wall St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['1 Line', 'Red', 'South Ferry', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to R Line'],
    # 2 Line (Red)
    ['2 Line', 'Red', 'Wakefield-241 St', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['2 Line', 'Red', '233 St', 'The Bronx', 'In Service', 'Yes', 'Yes', 'Metro-North interchange'],
    ['2 Line', 'Red', '225 St', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['2 Line', 'Red', '219 St', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['2 Line', 'Red', '215 St', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['2 Line', 'Red', '205 St', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['2 Line', 'Red', '198 St', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['2 Line', 'Red', '183 St', 'The Bronx', 'In Service', 'Yes', 'Yes', 'Transfer to 4 Line'],
    ['2 Line', 'Red', '174 St-175 St', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['2 Line', 'Red', '161 St-Yankee Stadium', 'The Bronx', 'In Service', 'Yes', 'Yes', 'Metro-North interchange'],
    ['2 Line', 'Red', '149 St-Grand Concourse', 'The Bronx', 'In Service', 'Yes', 'Yes', 'Transfer to 4/5 Lines'],
    ['2 Line', 'Red', '145 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['2 Line', 'Red', '135 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['2 Line', 'Red', '125 St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/3/A/B/C/D Lines'],
    ['2 Line', 'Red', '96 St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/3 Lines'],
    ['2 Line', 'Red', '86 St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/3 Lines'],
    ['2 Line', 'Red', '72 St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/3 Lines'],
    ['2 Line', 'Red', '59 St-Columbus Circle', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/3/A/B/C/D Lines'],
    ['2 Line', 'Red', '42 St-Port Authority Bus Terminal', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/3/A/C/E/N/Q/R/W Lines'],
    ['2 Line', 'Red', '34 St-Penn Station', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Amtrak/LIRR interchange'],
    ['2 Line', 'Red', '14 St-Union Square', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/3/N/Q/R/W/L Lines'],
    ['2 Line', 'Red', 'Flatbush Ave-Brooklyn College', 'Brooklyn', 'In Service', 'No', 'Yes', 'Southern Terminus'],
    # 4 Line (Green)
    ['4 Line', 'Green', 'Woodlawn', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', 'Mosholu Pkwy', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', 'Bedford Pk Blvd-Lehman College', 'The Bronx', 'In Service', 'No', 'Yes', 'Near Lehman College'],
    ['4 Line', 'Green', 'Gun Hill Rd', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', 'Burke Av', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', 'Pelham Pkwy', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', 'Morris Park', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', '183 St', 'The Bronx', 'In Service', 'Yes', 'Yes', 'Transfer to 2 Line'],
    ['4 Line', 'Green', '174 St-175 St', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', '161 St-Yankee Stadium', 'The Bronx', 'In Service', 'Yes', 'Yes', 'Metro-North interchange'],
    ['4 Line', 'Green', '149 St-Grand Concourse', 'The Bronx', 'In Service', 'Yes', 'Yes', 'Transfer to 2/5 Lines'],
    ['4 Line', 'Green', '138 St-Grand Concourse', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', '125 St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/2/3/A/B/C/D Lines'],
    ['4 Line', 'Green', '116 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', '86 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', '77 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', '59 St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to N/Q/R/W Lines'],
    ['4 Line', 'Green', '42 St-Grand Central Terminal', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Metro-North/LIRR interchange'],
    ['4 Line', 'Green', '33 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', '28 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', '23 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', '14 St-Union Square', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/2/3/N/Q/R/W/L Lines'],
    ['4 Line', 'Green', 'Bowery', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', 'Canal St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/A/C/E/N/Q/R/W Lines'],
    ['4 Line', 'Green', 'Fulton St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to A/C/J/Z/2/3 Lines'],
    ['4 Line', 'Green', 'Wall St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', 'Bowling Green', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', 'Broad St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', 'Nassau Ave', 'Brooklyn', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', 'Montrose Ave', 'Brooklyn', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', 'Clinton-Washington Aves', 'Brooklyn', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', 'Franklin Ave', 'Brooklyn', 'In Service', 'Yes', 'Yes', 'Transfer to C Line'],
    ['4 Line', 'Green', 'Nostrand Ave', 'Brooklyn', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', 'Utica Ave', 'Brooklyn', 'In Service', 'Yes', 'Yes', 'Transfer to A/C Lines'],
    ['4 Line', 'Green', 'Eastern Pkwy-Brooklyn Museum', 'Brooklyn', 'In Service', 'No', 'Yes', 'Near Brooklyn Museum'],
    ['4 Line', 'Green', 'President St-Medgar Evers College', 'Brooklyn', 'In Service', 'No', 'Yes', 'Near Medgar Evers College'],
    ['4 Line', 'Green', 'Sutter Av-Rutland Rd', 'Brooklyn', 'In Service', 'No', 'Yes', ''],
    ['4 Line', 'Green', 'Utica Ave', 'Brooklyn', 'In Service', 'Yes', 'Yes', 'Transfer to A/C Lines'],
    # A Line (Blue)
    ['A Line', 'Blue', 'Inwood-207 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', '190 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', '181 St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1 Line'],
    ['A Line', 'Blue', '175 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', '168 St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1 Line'],
    ['A Line', 'Blue', '155 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', '145 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', '125 St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/2/3/B/C/D Lines'],
    ['A Line', 'Blue', '110 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', '96 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', '86 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', '79 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', '72 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', '59 St-Columbus Circle', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/2/3/B/C/D Lines'],
    ['A Line', 'Blue', '50 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', '42 St-Port Authority Bus Terminal', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/2/3/C/E/N/Q/R/W Lines'],
    ['A Line', 'Blue', '34 St-Penn Station', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Amtrak/LIRR interchange'],
    ['A Line', 'Blue', '23 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', '14 St-Union Square', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/2/3/N/Q/R/W/L Lines'],
    ['A Line', 'Blue', '8 St-NYU', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', 'Canal St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/2/3/E/N/Q/R/W Lines'],
    ['A Line', 'Blue', 'Chambers St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', 'Fulton St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 2/3/4/5/J/Z Lines'],
    ['A Line', 'Blue', 'Broad St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', 'Wall St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', 'Fulton St', 'Brooklyn', 'In Service', 'Yes', 'Yes', 'Transfer to C/J/Z Lines'],
    ['A Line', 'Blue', 'Nostrand Ave', 'Brooklyn', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', 'Utica Ave', 'Brooklyn', 'In Service', 'Yes', 'Yes', 'Transfer to 4/5 Lines'],
    ['A Line', 'Blue', 'Kingston Av', 'Brooklyn', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', 'Crown Heights-Utica Av', 'Brooklyn', 'In Service', 'Yes', 'Yes', 'Transfer to 3 Line'],
    ['A Line', 'Blue', 'Sutter Av-Rutland Rd', 'Brooklyn', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', 'Rockaway Av', 'Brooklyn', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', 'Broadway Junction', 'Brooklyn', 'In Service', 'Yes', 'Yes', 'Transfer to J/Z/L Lines'],
    ['A Line', 'Blue', 'Liberty Av', 'Brooklyn', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', 'Rockaway Blvd', 'Queens', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', '80 St', 'Queens', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', '88 St', 'Queens', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', '96 St', 'Queens', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', '104 St', 'Queens', 'In Service', 'No', 'Yes', ''],
    ['A Line', 'Blue', 'Rockaway Park-Beach 116 St', 'Queens', 'In Service', 'No', 'Yes', ''],
    # B Line (Orange)
    ['B Line', 'Orange', 'Bedford Park Blvd-Lehman College', 'The Bronx', 'In Service', 'No', 'Yes', 'Near Lehman College'],
    ['B Line', 'Orange', 'Mosholu Pkwy', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['B Line', 'Orange', '207 St', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['B Line', 'Orange', '191 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['B Line', 'Orange', '181 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['B Line', 'Orange', '168 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['B Line', 'Orange', '155 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['B Line', 'Orange', '145 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['B Line', 'Orange', '125 St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/2/3/A/C/D Lines'],
    ['B Line', 'Orange', '96 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['B Line', 'Orange', '86 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['B Line', 'Orange', '72 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['B Line', 'Orange', '59 St-Columbus Circle', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/2/3/A/C/D Lines'],
    ['B Line', 'Orange', '50 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['B Line', 'Orange', '42 St-Port Authority Bus Terminal', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/2/3/A/C/E/N/Q/R/W Lines'],
    ['B Line', 'Orange', '34 St-Herald Square', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to N/Q/R/W Lines'],
    ['B Line', 'Orange', '23 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['B Line', 'Orange', '14 St-Union Square', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/2/3/N/Q/R/W/L Lines'],
    ['B Line', 'Orange', 'West 4 St-Washington Square', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to A/C/E Lines'],
    ['B Line', 'Orange', 'Broadway-Lafayette St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to F/V Lines'],
    ['B Line', 'Orange', 'Prince St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['B Line', 'Orange', 'Spring St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['B Line', 'Orange', 'Canal St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/A/C/E/N/Q/R/W Lines'],
    # C Line (Blue)
    ['C Line', 'Blue', '168 St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1 Line'],
    ['C Line', 'Blue', '155 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['C Line', 'Blue', '145 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['C Line', 'Blue', '125 St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/2/3/B/D Lines'],
    ['C Line', 'Blue', '110 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['C Line', 'Blue', '96 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['C Line', 'Blue', '86 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['C Line', 'Blue', '72 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['C Line', 'Blue', '59 St-Columbus Circle', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/2/3/A/B/D Lines'],
    ['C Line', 'Blue', '50 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['C Line', 'Blue', '42 St-Port Authority Bus Terminal', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/2/3/A/E/N/Q/R/W Lines'],
    ['C Line', 'Blue', '34 St-Penn Station', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Amtrak/LIRR interchange'],
    ['C Line', 'Blue', '23 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['C Line', 'Blue', '14 St-Union Square', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/2/3/N/Q/R/W/L Lines'],
    ['C Line', 'Blue', '8 St-NYU', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['C Line', 'Blue', 'Canal St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/A/E/N/Q/R/W Lines'],
    ['C Line', 'Blue', 'Chambers St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['C Line', 'Blue', 'Fulton St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 2/3/4/5/J/Z Lines'],
    ['C Line', 'Blue', 'Broad St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['C Line', 'Blue', 'Wall St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['C Line', 'Blue', 'Fulton St', 'Brooklyn', 'In Service', 'Yes', 'Yes', 'Transfer to A/J/Z Lines'],
    ['C Line', 'Blue', 'Nostrand Ave', 'Brooklyn', 'In Service', 'No', 'Yes', ''],
    ['C Line', 'Blue', 'Utica Ave', 'Brooklyn', 'In Service', 'Yes', 'Yes', 'Transfer to 4/5 Lines'],
    ['C Line', 'Blue', 'Kingston Av', 'Brooklyn', 'In Service', 'No', 'Yes', ''],
    ['C Line', 'Blue', 'Crown Heights-Utica Av', 'Brooklyn', 'In Service', 'Yes', 'Yes', 'Transfer to 3 Line'],
    ['C Line', 'Blue', 'Sutter Av-Rutland Rd', 'Brooklyn', 'In Service', 'No', 'Yes', ''],
    ['C Line', 'Blue', 'Rockaway Av', 'Brooklyn', 'In Service', 'No', 'Yes', ''],
    ['C Line', 'Blue', 'Broadway Junction', 'Brooklyn', 'In Service', 'Yes', 'Yes', 'Transfer to J/Z/L Lines'],
    # D Line (Orange)
    ['D Line', 'Orange', 'Norwood-205 St', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['D Line', 'Orange', 'Bedford Park Blvd-Lehman College', 'The Bronx', 'In Service', 'No', 'Yes', 'Near Lehman College'],
    ['D Line', 'Orange', 'Mosholu Pkwy', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['D Line', 'Orange', '207 St', 'The Bronx', 'In Service', 'No', 'Yes', ''],
    ['D Line', 'Orange', '191 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['D Line', 'Orange', '181 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['D Line', 'Orange', '168 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['D Line', 'Orange', '155 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['D Line', 'Orange', '145 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['D Line', 'Orange', '125 St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/2/3/A/C/B Lines'],
    ['D Line', 'Orange', '96 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['D Line', 'Orange', '86 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['D Line', 'Orange', '72 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['D Line', 'Orange', '59 St-Columbus Circle', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/2/3/A/C/B Lines'],
    ['D Line', 'Orange', '50 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['D Line', 'Orange', '42 St-Port Authority Bus Terminal', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/2/3/A/C/E/N/Q/R/W Lines'],
    ['D Line', 'Orange', '34 St-Herald Square', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to N/Q/R/W Lines'],
    ['D Line', 'Orange', '23 St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['D Line', 'Orange', '14 St-Union Square', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/2/3/N/Q/R/W/L Lines'],
    ['D Line', 'Orange', 'West 4 St-Washington Square', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to A/C/E Lines'],
    ['D Line', 'Orange', 'Broadway-Lafayette St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to F/V Lines'],
    ['D Line', 'Orange', 'Prince St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['D Line', 'Orange', 'Spring St', 'Manhattan', 'In Service', 'No', 'Yes', ''],
    ['D Line', 'Orange', 'Canal St', 'Manhattan', 'In Service', 'Yes', 'Yes', 'Transfer to 1/A/C/E/N/Q/R/W Lines'],
    ['D Line', 'Orange', 'Bay Ridge-95 St', 'Brooklyn', 'In Service', 'No', 'Yes', 'Southern Terminus'],
    # JFK Airport Access
    ['AirTrain JFK', 'Light Blue', 'Jamaica Van Wyck', 'Queens', 'In Service', 'Yes', 'Yes', 'Transfer to E Line'],
    ['AirTrain JFK', 'Light Blue', 'Sutphin Blvd-Archer Av-JFK Airport', 'Queens', 'In Service', 'Yes', 'Yes', 'LIRR interchange, JFK Airport connection'],
    # Special Stations
    ['LIRR', 'None', 'Jamaica', 'Queens', 'In Service', 'Yes', 'Yes', 'Transfer to AirTrain JFK/E/J/Z Lines'],
    ['Metro-North', 'None', 'The Bronx Stations', 'The Bronx', 'In Service', 'Yes', 'Yes', 'Transfer to 1/2/4 Lines'],
    ['Staten Island Railway', 'None', 'Staten Island Stations', 'Staten Island', 'In Service', 'Varies', 'Yes', 'No direct subway connection'],
    ['Canarsie Line (L)', 'Gray', 'Canarsie-Rockaway Pkwy', 'Brooklyn', 'In Service', 'No', 'Yes', 'Eastern Terminus'],
    ['Rockaway Line', 'None', 'Rockaway Pkwy', 'Brooklyn', 'In Service', 'Yes', 'Yes', 'Transfer to L Line']
]

import json
import re
from collections import defaultdict
from typing import Dict, List, Tuple


BAD_STATION_NAMES = {
    "The Bronx Stations",
    "Staten Island Stations",
}

def clean_name(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def slug_station(name: str) -> str:
    s = clean_name(name).lower()
    s = s.replace("&", "and")
    s = s.replace("'", "")
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return f"st_{s}"

def is_valid_row(row: List[str]) -> bool:
    if len(row) < 8:
        return False
    station_name = clean_name(row[2])
    if not station_name:
        return False
    if station_name in BAD_STATION_NAMES:
        return False
    # 过滤明显的“集合项”
    if station_name.lower().endswith(" stations"):
        return False
    return True


def build_graph_from_nyc_data(nyc_subway_data: List[List[str]]) -> Tuple[List[dict], List[dict], Dict[str, Dict[str, float]]]:
    if not nyc_subway_data or len(nyc_subway_data) < 2:
        raise ValueError("nyc_subway_data is empty")

    rows = nyc_subway_data[1:]  # skip header

    line_seq: Dict[str, List[str]] = defaultdict(list)
    station_info: Dict[str, dict] = {}

    for r in rows:
        if not is_valid_row(r):
            continue

        line_name = clean_name(r[0])
        line_color = clean_name(r[1])
        station_name = clean_name(r[2])
        borough = clean_name(r[3])
        station_status = clean_name(r[4])
        transfer_station = clean_name(r[5])
        accessible = clean_name(r[6])
        remarks = clean_name(r[7])

        sid = slug_station(station_name)

        if sid not in station_info:
            station_info[sid] = {
                "station_id": sid,
                "station_name": station_name,
                "lines": set(),
                "boroughs": set(),
                "station_status": set(),
                "transfer_station": set(),
                "accessible": set(),
                "remarks": set(),
            }

        station_info[sid]["lines"].add(line_name)
        if borough: station_info[sid]["boroughs"].add(borough)
        if station_status: station_info[sid]["station_status"].add(station_status)
        if transfer_station: station_info[sid]["transfer_station"].add(transfer_station)
        if accessible: station_info[sid]["accessible"].add(accessible)
        if remarks: station_info[sid]["remarks"].add(remarks)

        if not line_seq[line_name] or line_seq[line_name][-1] != sid:
            line_seq[line_name].append(sid)

    edges: List[dict] = []
    seen = set()
    for line_name, seq in line_seq.items():
        for a, b in zip(seq[:-1], seq[1:]):
            key = (a, b, line_name)
            if key in seen:
                continue
            seen.add(key)
            edges.append({
                "from_station_id": a,
                "to_station_id": b,
                "line_name": line_name,
                "weight": 1,
                "bidirectional": 1,
            })

    adj: Dict[str, Dict[str, float]] = defaultdict(dict)
    for e in edges:
        a, b, w = e["from_station_id"], e["to_station_id"], float(e["weight"])
        adj[a][b] = min(adj[a].get(b, w), w)
        if e.get("bidirectional", 1):
            adj[b][a] = min(adj[b].get(a, w), w)

    stations: List[dict] = []
    for s in station_info.values():
        stations.append({
            "station_id": s["station_id"],
            "station_name": s["station_name"],
            "lines": "|".join(sorted(s["lines"])),
            "boroughs": "|".join(sorted(s["boroughs"])) if s["boroughs"] else "",
            "station_status": "|".join(sorted(s["station_status"])) if s["station_status"] else "",
            "transfer_station": "|".join(sorted(s["transfer_station"])) if s["transfer_station"] else "",
            "accessible": "|".join(sorted(s["accessible"])) if s["accessible"] else "",
            "remarks": "|".join(sorted(s["remarks"])) if s["remarks"] else "",
        })

    return stations, edges, dict(adj)


def write_csv(path: str, rows: List[dict], fieldnames: List[str]):
    import csv
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        w.writerows(rows)


def main():
    stations, edges, adj = build_graph_from_nyc_data(nyc_subway_data)

    write_csv(
        "nyc_subway_stations.csv",
        stations,
        ["station_id", "station_name", "lines", "boroughs", "station_status", "transfer_station", "accessible", "remarks"],
    )
    write_csv(
        "nyc_subway_edges.csv",
        edges,
        ["from_station_id", "to_station_id", "line_name", "weight", "bidirectional"],
    )
    with open("nyc_subway_adjacency.json", "w", encoding="utf-8") as f:
        json.dump(adj, f, ensure_ascii=False)

    print(f"OK: stations={len(stations)}, edges={len(edges)}")
    print("Wrote: nyc_subway_stations.csv, nyc_subway_edges.csv, nyc_subway_adjacency.json")


if __name__ == "__main__":
    main()
