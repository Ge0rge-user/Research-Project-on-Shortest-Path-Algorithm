# -*- coding: utf-8 -*-
"""
london_tube_graph_export.py

做“同样的事”：在不改变你原始 london_tube_data 的前提下，
把它转换成“图数据”并输出 CSV/JSON，满足最短路算法输入。

输入：
- london_tube_data（你原文件里的表格数据，已原样粘贴）

输出（运行后在当前目录生成）：
- london_tube_stations.csv      (station_id, station_name, lines, fare_zones, station_status, transfer_station, accessible, remarks)
- london_tube_edges.csv         (from_station_id, to_station_id, line_name, weight, bidirectional)
- london_tube_adjacency.json    (邻接表)

规则（最小必要改动）：
- station_id 由站名生成（同名换乘站自动合并）
- 按每条 Line 的出现顺序连相邻站为边（weight=1）
- 过滤明显不是“具体站点”的占位项（如 'Liberty Line Stations' 这类）
"""

import csv

london_tube_data = [
    ['Line Name', 'Line Color', 'Station Name', 'Fare Zones', 'Station Status', 'Transfer Station', 'Accessible', 'Remarks'],
    # Bakerloo Line
    ['Bakerloo Line', 'Brown', 'Harrow & Wealdstone', 'Zone 5', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['Bakerloo Line', 'Brown', 'Kenton', 'Zone 4/5', 'In Service', 'No', 'Yes', ''],
    ['Bakerloo Line', 'Brown', 'South Kenton', 'Zone 4', 'In Service', 'No', 'Yes', ''],
    ['Bakerloo Line', 'Brown', 'North Wembley', 'Zone 4', 'In Service', 'No', 'Yes', ''],
    ['Bakerloo Line', 'Brown', 'Wembley Central', 'Zone 4', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['Bakerloo Line', 'Brown', 'Stonebridge Park', 'Zone 3/4', 'In Service', 'No', 'Yes', ''],
    ['Bakerloo Line', 'Brown', 'Harlesden', 'Zone 3', 'In Service', 'No', 'Yes', ''],
    ['Bakerloo Line', 'Brown', 'Willesden Junction', 'Zone 3', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['Bakerloo Line', 'Brown', 'Kensal Green', 'Zone 2/3', 'In Service', 'No', 'Yes', ''],
    ['Bakerloo Line', 'Brown', 'Queen\'s Park', 'Zone 2', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['Bakerloo Line', 'Brown', 'Kilburn Park', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['Bakerloo Line', 'Brown', 'Maida Vale', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['Bakerloo Line', 'Brown', 'Warwick Avenue', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['Bakerloo Line', 'Brown', 'Paddington', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Central/ Hammersmith & City/Metropolitan Lines'],
    ['Bakerloo Line', 'Brown', 'Edgware Road (Bakerloo)', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['Bakerloo Line', 'Brown', 'Marylebone', 'Zone 1', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['Bakerloo Line', 'Brown', 'Baker Street', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Central/ Hammersmith & City/Metropolitan/ Jubilee Lines'],
    ['Bakerloo Line', 'Brown', 'Portland Place', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['Bakerloo Line', 'Brown', 'Regent\'s Park', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['Bakerloo Line', 'Brown', 'Oxford Circus', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Central/Victoria Lines'],
    ['Bakerloo Line', 'Brown', 'Piccadilly Circus', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Piccadilly Line'],
    ['Bakerloo Line', 'Brown', 'Leicester Square', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Northern Line'],
    ['Bakerloo Line', 'Brown', 'Covent Garden', 'Zone 1', 'In Service', 'No', 'No', ''],
    ['Bakerloo Line', 'Brown', 'Holborn', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Central Line'],
    ['Bakerloo Line', 'Brown', 'Charing Cross', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Northern/Bakerloo Lines'],
    ['Bakerloo Line', 'Brown', 'Embankment', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Northern/District/Circle Lines'],
    ['Bakerloo Line', 'Brown', 'Waterloo', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Northern/Jubilee/Waterloo & City Lines'],
    ['Bakerloo Line', 'Brown', 'Elephant & Castle', 'Zone 1/2', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    # Central Line
    ['Central Line', 'Red', 'Epping', 'Zone 6', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Theydon Bois', 'Zone 6', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Debden', 'Zone 6', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Loughton', 'Zone 6', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['Central Line', 'Red', 'Buckhurst Hill', 'Zone 5/6', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Woodford', 'Zone 5', 'In Service', 'Yes', 'Yes', 'Transfer to Hainault Loop'],
    ['Central Line', 'Red', 'South Woodford', 'Zone 4/5', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Snaresbrook', 'Zone 4', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Leytonstone', 'Zone 3/4', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Leyton', 'Zone 3', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Stratford', 'Zone 2/3', 'In Service', 'Yes', 'Yes', 'National Rail/DLR interchange'],
    ['Central Line', 'Red', 'Mile End', 'Zone 2/3', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Bow Road', 'Zone 2/3', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Mile End', 'Zone 2/3', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Bethnal Green', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Shoreditch High Street', 'Zone 1/2', 'In Service', 'Yes', 'Yes', 'DLR interchange'],
    ['Central Line', 'Red', 'Liverpool Street', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Circle/Metropolitan/Hammersmith & City/Waterloo & City Lines'],
    ['Central Line', 'Red', 'Bank', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Northern/DLR Lines'],
    ['Central Line', 'Red', 'St. Paul\'s', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Chancery Lane', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Holborn', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Bakerloo/Piccadilly Lines'],
    ['Central Line', 'Red', 'Tottenham Court Road', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Northern Line'],
    ['Central Line', 'Red', 'Oxford Circus', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Bakerloo/Victoria Lines'],
    ['Central Line', 'Red', 'Bond Street', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Jubilee Line'],
    ['Central Line', 'Red', 'Marble Arch', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Lancaster Gate', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Paddington', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Bakerloo/Hammersmith & City/Metropolitan Lines'],
    ['Central Line', 'Red', 'Queensway', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Bayswater', 'Zone 1/2', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Notting Hill Gate', 'Zone 1/2', 'In Service', 'Yes', 'Yes', 'Transfer to District/Circle Lines'],
    ['Central Line', 'Red', 'Holland Park', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Shepherd\'s Bush (Central)', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'White City', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'East Acton', 'Zone 2/3', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'North Acton', 'Zone 3', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'West Acton', 'Zone 3', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Ealing Broadway', 'Zone 3', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['Central Line', 'Red', 'Ealing Common', 'Zone 3', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Acton Town', 'Zone 3', 'In Service', 'Yes', 'Yes', 'Transfer to Piccadilly Line'],
    ['Central Line', 'Red', 'Chiswick Park', 'Zone 3', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Turnham Green', 'Zone 2/3', 'In Service', 'Yes', 'Yes', 'Transfer to District Line'],
    ['Central Line', 'Red', 'Stamford Brook', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Ravenscourt Park', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['Central Line', 'Red', 'Hammersmith', 'Zone 2', 'In Service', 'Yes', 'Yes', 'Transfer to District/Circle/Hammersmith & City Lines'],
    # Circle Line
    ['Circle Line', 'Yellow', 'Edgware Road (Circle)', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Hammersmith & City/Metropolitan Lines'],
    ['Circle Line', 'Yellow', 'Paddington', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Bakerloo/Central/Hammersmith & City/Metropolitan Lines'],
    ['Circle Line', 'Yellow', 'Bayswater', 'Zone 1/2', 'In Service', 'No', 'Yes', ''],
    ['Circle Line', 'Yellow', 'Notting Hill Gate', 'Zone 1/2', 'In Service', 'Yes', 'Yes', 'Transfer to Central/District Lines'],
    ['Circle Line', 'Yellow', 'High Street Kensington', 'Zone 1/2', 'In Service', 'Yes', 'Yes', 'Transfer to District Line'],
    ['Circle Line', 'Yellow', 'Kensington (Olympia)', 'Zone 2', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['Circle Line', 'Yellow', 'Earl\'s Court', 'Zone 1/2', 'In Service', 'Yes', 'Yes', 'Transfer to District/Piccadilly Lines'],
    ['Circle Line', 'Yellow', 'Gloucester Road', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to District/Piccadilly Lines'],
    ['Circle Line', 'Yellow', 'South Kensington', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to District/Piccadilly Lines'],
    ['Circle Line', 'Yellow', 'Sloane Square', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['Circle Line', 'Yellow', 'Victoria', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Victoria Line'],
    ['Circle Line', 'Yellow', 'St. James\'s Park', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['Circle Line', 'Yellow', 'Westminster', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Jubilee Line'],
    ['Circle Line', 'Yellow', 'Embankment', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Bakerloo/Northern/District Lines'],
    ['Circle Line', 'Yellow', 'Temple', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['Circle Line', 'Yellow', 'Blackfriars', 'Zone 1', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['Circle Line', 'Yellow', 'Mansion House', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['Circle Line', 'Yellow', 'Bank', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Central/Northern/DLR Lines'],
    ['Circle Line', 'Yellow', 'Monument', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to District Line'],
    ['Circle Line', 'Yellow', 'Tower Hill', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['Circle Line', 'Yellow', 'Aldgate East', 'Zone 1/2', 'In Service', 'Yes', 'Yes', 'Transfer to Hammersmith & City Line'],
    ['Circle Line', 'Yellow', 'Aldgate', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Metropolitan Line'],
    ['Circle Line', 'Yellow', 'Liverpool Street', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Central/Hammersmith & City/Metropolitan/Waterloo & City Lines'],
    ['Circle Line', 'Yellow', 'Moorgate', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Metropolitan/Hammersmith & City Lines'],
    # District Line
    ['District Line', 'Green', 'Upminster', 'Zone 6', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['District Line', 'Green', 'Upminster Bridge', 'Zone 6', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Rainham', 'Zone 6', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Purfleet', 'Zone 6', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Grays', 'Zone 6', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['District Line', 'Green', 'Tilbury Town', 'Zone 6', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'East Tilbury', 'Zone 6', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Stanford-le-Hope', 'Zone 6', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['District Line', 'Green', 'Pitsea', 'Zone 6', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Benfleet', 'Zone 6', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['District Line', 'Green', 'Leigh-on-Sea', 'Zone 6', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Chalkwell', 'Zone 6', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Westcliff-on-Sea', 'Zone 6', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Southend Central', 'Zone 6', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Southend East', 'Zone 6', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Shoeburyness', 'Zone 6', 'In Service', 'No', 'Yes', 'Eastern Terminus'],
    ['District Line', 'Green', 'Barking', 'Zone 4', 'In Service', 'Yes', 'Yes', 'National Rail/DLR interchange'],
    ['District Line', 'Green', 'East Ham', 'Zone 3/4', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Upton Park', 'Zone 3', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Plaistow', 'Zone 3', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'West Ham', 'Zone 2/3', 'In Service', 'Yes', 'Yes', 'National Rail/DLR interchange'],
    ['District Line', 'Green', 'Mile End', 'Zone 2/3', 'In Service', 'Yes', 'Yes', 'Transfer to Central Line'],
    ['District Line', 'Green', 'Bow Road', 'Zone 2/3', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Aldgate East', 'Zone 1/2', 'In Service', 'Yes', 'Yes', 'Transfer to Circle/Hammersmith & City Lines'],
    ['District Line', 'Green', 'Tower Hill', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Monument', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Circle/Northern Lines'],
    ['District Line', 'Green', 'Cannon Street', 'Zone 1', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['District Line', 'Green', 'Mansion House', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Blackfriars', 'Zone 1', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['District Line', 'Green', 'Temple', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Embankment', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Bakerloo/Circle/Northern Lines'],
    ['District Line', 'Green', 'Westminster', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Circle/Jubilee Lines'],
    ['District Line', 'Green', 'St. James\'s Park', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Victoria', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Circle/Victoria Lines'],
    ['District Line', 'Green', 'Sloane Square', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'South Kensington', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Circle/Piccadilly Lines'],
    ['District Line', 'Green', 'Gloucester Road', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Circle/Piccadilly Lines'],
    ['District Line', 'Green', 'Earl\'s Court', 'Zone 1/2', 'In Service', 'Yes', 'Yes', 'Transfer to Circle/Piccadilly Lines'],
    ['District Line', 'Green', 'West Kensington', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Barons Court', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Hammersmith', 'Zone 2', 'In Service', 'Yes', 'Yes', 'Transfer to Central/Circle/Hammersmith & City Lines'],
    ['District Line', 'Green', 'Turnham Green', 'Zone 2/3', 'In Service', 'Yes', 'Yes', 'Transfer to Central Line'],
    ['District Line', 'Green', 'Stamford Brook', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Ravenscourt Park', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Chiswick Park', 'Zone 3', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Acton Town', 'Zone 3', 'In Service', 'Yes', 'Yes', 'Transfer to Central/Piccadilly Lines'],
    ['District Line', 'Green', 'Ealing Common', 'Zone 3', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Ealing Broadway', 'Zone 3', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['District Line', 'Green', 'South Ealing', 'Zone 3', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'North Ealing', 'Zone 3', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Hanger Lane', 'Zone 3/4', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Perivale', 'Zone 4', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'Greenford', 'Zone 4', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['District Line', 'Green', 'Northolt', 'Zone 5', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'South Ruislip', 'Zone 5', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['District Line', 'Green', 'Ruislip Gardens', 'Zone 5', 'In Service', 'No', 'Yes', ''],
    ['District Line', 'Green', 'West Ruislip', 'Zone 6', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    # Northern Line
    ['Northern Line', 'Black', 'Edgware', 'Zone 5', 'In Service', 'No', 'Yes', ''],
    ['Northern Line', 'Black', 'Burnt Oak', 'Zone 4/5', 'In Service', 'No', 'Yes', ''],
    ['Northern Line', 'Black', 'Colindale', 'Zone 4', 'In Service', 'No', 'Yes', ''],
    ['Northern Line', 'Black', 'Kingsbury', 'Zone 4', 'In Service', 'No', 'Yes', ''],
    ['Northern Line', 'Black', 'Wembley Park', 'Zone 4', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['Northern Line', 'Black', 'Stonebridge Park', 'Zone 3/4', 'In Service', 'No', 'Yes', ''],
    ['Northern Line', 'Black', 'Harlesden', 'Zone 3', 'In Service', 'No', 'Yes', ''],
    ['Northern Line', 'Black', 'Willesden Green', 'Zone 2/3', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['Northern Line', 'Black', 'Kilburn', 'Zone 2/3', 'In Service', 'No', 'Yes', ''],
    ['Northern Line', 'Black', 'West Hampstead', 'Zone 2', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['Northern Line', 'Black', 'Finchley Road', 'Zone 2', 'In Service', 'Yes', 'Yes', 'Transfer to Metropolitan Line'],
    ['Northern Line', 'Black', 'Swiss Cottage', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['Northern Line', 'Black', 'St. John\'s Wood', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['Northern Line', 'Black', 'Baker Street', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Bakerloo/Central/Hammersmith & City/Metropolitan/Jubilee Lines'],
    ['Northern Line', 'Black', 'Great Portland Street', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['Northern Line', 'Black', 'Euston', 'Zone 1', 'In Service', 'Yes', 'Yes', 'National Rail/ Victoria Line interchange'],
    ['Northern Line', 'Black', 'Warren Street', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Victoria Line'],
    ['Northern Line', 'Black', 'Goodge Street', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['Northern Line', 'Black', 'Tottenham Court Road', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Central Line'],
    ['Northern Line', 'Black', 'Leicester Square', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Bakerloo Line'],
    ['Northern Line', 'Black', 'Charing Cross', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Bakerloo/Circle/District Lines'],
    ['Northern Line', 'Black', 'Embankment', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Bakerloo/Circle/District Lines'],
    ['Northern Line', 'Black', 'Waterloo', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Bakerloo/Jubilee/Waterloo & City Lines'],
    ['Northern Line', 'Black', 'Kennington', 'Zone 1/2', 'In Service', 'Yes', 'Yes', 'Transfer to Charing Cross/Bank Branches'],
    ['Northern Line', 'Black', 'Oval', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['Northern Line', 'Black', 'Stockwell', 'Zone 2', 'In Service', 'Yes', 'Yes', 'Transfer to Victoria Line'],
    ['Northern Line', 'Black', 'Clapham North', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['Northern Line', 'Black', 'Clapham Common', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['Northern Line', 'Black', 'Clapham South', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['Northern Line', 'Black', 'Balham', 'Zone 3', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['Northern Line', 'Black', 'Tooting Bec', 'Zone 3', 'In Service', 'No', 'Yes', ''],
    ['Northern Line', 'Black', 'Tooting Broadway', 'Zone 3', 'In Service', 'No', 'Yes', ''],
    ['Northern Line', 'Black', 'Colliers Wood', 'Zone 3', 'In Service', 'No', 'Yes', ''],
    ['Northern Line', 'Black', 'South Wimbledon', 'Zone 3', 'In Service', 'No', 'Yes', ''],
    ['Northern Line', 'Black', 'Morden', 'Zone 4', 'In Service', 'No', 'Yes', 'Southern Terminus'],
    # Elizabeth Line
    ['Elizabeth Line', 'Purple', 'Heathrow Terminal 4', 'Outside Fare Zones', 'In Service', 'No', 'Yes', 'Special fares apply'],
    ['Elizabeth Line', 'Purple', 'Heathrow Terminal 5', 'Outside Fare Zones', 'In Service', 'No', 'Yes', 'Special fares apply'],
    ['Elizabeth Line', 'Purple', 'Heathrow Terminals 2 & 3', 'Outside Fare Zones', 'In Service', 'No', 'Yes', 'Special fares apply'],
    ['Elizabeth Line', 'Purple', 'Terminal 5', 'Outside Fare Zones', 'In Service', 'No', 'Yes', 'Special fares apply'],
    ['Elizabeth Line', 'Purple', 'Slough', 'Zone 6', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['Elizabeth Line', 'Purple', 'Langley', 'Zone 6', 'In Service', 'No', 'Yes', ''],
    ['Elizabeth Line', 'Purple', 'Iver', 'Zone 6', 'In Service', 'No', 'Yes', ''],
    ['Elizabeth Line', 'Purple', 'West Drayton', 'Zone 6', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['Elizabeth Line', 'Purple', 'Hayes & Harlington', 'Zone 5/6', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['Elizabeth Line', 'Purple', 'Southall', 'Zone 5', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['Elizabeth Line', 'Purple', 'Hanwell', 'Zone 5', 'In Service', 'No', 'Yes', ''],
    ['Elizabeth Line', 'Purple', 'Ealing Broadway', 'Zone 3', 'In Service', 'Yes', 'Yes', 'Transfer to Central/District Lines'],
    ['Elizabeth Line', 'Purple', 'Ealing Broadway', 'Zone 3', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['Elizabeth Line', 'Purple', 'Acton Main Line', 'Zone 3', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['Elizabeth Line', 'Purple', 'Paddington', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Bakerloo/Central/Circle/Hammersmith & City/Metropolitan Lines'],
    ['Elizabeth Line', 'Purple', 'Bond Street', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Central/Jubilee Lines'],
    ['Elizabeth Line', 'Purple', 'Tottenham Court Road', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Central/Northern Lines'],
    ['Elizabeth Line', 'Purple', 'Farringdon', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Hammersmith & City/Metropolitan Lines'],
    ['Elizabeth Line', 'Purple', 'Liverpool Street', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Central/Circle/Hammersmith & City/Metropolitan/Waterloo & City Lines'],
    ['Elizabeth Line', 'Purple', 'Whitechapel', 'Zone 1/2', 'In Service', 'Yes', 'Yes', 'Transfer to District/Hammersmith & City Lines'],
    ['Elizabeth Line', 'Purple', 'Stepney Green', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['Elizabeth Line', 'Purple', 'Mile End', 'Zone 2/3', 'In Service', 'Yes', 'Yes', 'Transfer to Central/District Lines'],
    ['Elizabeth Line', 'Purple', 'Bow Road', 'Zone 2/3', 'In Service', 'No', 'Yes', ''],
    ['Elizabeth Line', 'Purple', 'Stratford', 'Zone 2/3', 'In Service', 'Yes', 'Yes', 'Transfer to Central/DLR Lines'],
    ['Elizabeth Line', 'Purple', 'Shenfield', 'Zone 6+', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    # DLR
    ['DLR', 'Turquoise', 'Bank', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Central/Northern/Circle Lines'],
    ['DLR', 'Turquoise', 'Monument', 'Zone 1', 'In Service', 'Yes', 'Yes', 'Transfer to Circle/District/Northern Lines'],
    ['DLR', 'Turquoise', 'Tower Gateway', 'Zone 1', 'In Service', 'No', 'Yes', ''],
    ['DLR', 'Turquoise', 'Shadwell', 'Zone 1/2', 'In Service', 'No', 'Yes', ''],
    ['DLR', 'Turquoise', 'Wapping', 'Zone 1/2', 'In Service', 'No', 'Yes', ''],
    ['DLR', 'Turquoise', 'Rotherhithe', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['DLR', 'Turquoise', 'Canada Water', 'Zone 2', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['DLR', 'Turquoise', 'Surrey Quays', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['DLR', 'Turquoise', 'Deptford Bridge', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['DLR', 'Turquoise', 'Elverson Road', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['DLR', 'Turquoise', 'Lewisham', 'Zone 2', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['DLR', 'Turquoise', 'Island Gardens', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['DLR', 'Turquoise', 'Cutty Sark for Maritime Greenwich', 'Zone 2', 'Temporarily Closed', 'Yes', 'No', 'Closed until spring 2026'],
    ['DLR', 'Turquoise', 'Greenwich', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['DLR', 'Turquoise', 'Maze Hill', 'Zone 2', 'In Service', 'No', 'Yes', ''],
    ['DLR', 'Turquoise', 'Charlton', 'Zone 3', 'In Service', 'No', 'Yes', ''],
    ['DLR', 'Turquoise', 'Woolwich Arsenal', 'Zone 4', 'In Service', 'Yes', 'Yes', 'National Rail interchange'],
    ['DLR', 'Turquoise', 'Plumstead', 'Zone 4', 'In Service', 'No', 'Yes', ''],
    ['DLR', 'Turquoise', ' Abbey Wood', 'Zone 4', 'In Service', 'Yes', 'Yes', 'Elizabeth Line interchange'],
    # Special Status Stations
    ['Hounslow West', 'Unknown', 'Hounslow West', 'Zone 4', 'In Service', 'No', 'Partial', 'Step-free access for manual wheelchairs only'],
    ['IFS Cloud Cable Car', 'Blue', 'IFS Cloud Cable Car', 'Outside Fare Zones', 'In Service', 'No', 'Yes', 'Special fares apply'],
    ['Liberty Line', 'Red/White/Blue', 'Liberty Line Stations', 'Varies', 'In Service', 'Varies', 'Yes', ''],
    ['Lioness Line', 'Blue/White', 'Lioness Line Stations', 'Varies', 'In Service', 'Varies', 'Yes', ''],
    ['Mildmay Line', 'Purple/White', 'Mildmay Line Stations', 'Varies', 'In Service', 'Varies', 'Yes', ''],
    ['Suffragette Line', 'Green/White', 'Suffragette Line Stations', 'Varies', 'In Service', 'Varies', 'Yes', ''],
    ['Weaver Line', 'Yellow/Black', 'Weaver Line Stations', 'Varies', 'In Service', 'Varies', 'Yes', ''],
    ['Windrush Line', 'Red/Gold', 'Windrush Line Stations', 'Varies', 'In Service', 'Varies', 'Yes', '']
]

import json
import re
from collections import defaultdict
from typing import Dict, List, Tuple


# 明显不是具体站点的占位/集合项（你的数据末尾就有这些）
BAD_STATION_NAMES = {
    "Liberty Line Stations",
    "Lioness Line Stations",
    "Mildmay Line Stations",
    "Suffragette Line Stations",
    "Weaver Line Stations",
    "Windrush Line Stations",
    "IFS Cloud Cable Car",  # 不是地铁站点（若你要保留可从这里移除）
}

def clean_name(name: str) -> str:
    return re.sub(r"\s+", " ", (name or "").strip())

def slug_station(name: str) -> str:
    """把站名转成稳定 id：同名站会合并"""
    s = clean_name(name).lower()
    s = s.replace("&", "and")
    s = s.replace("'", "")
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return f"st_{s}"

def is_valid_row(row: List[str]) -> bool:
    """过滤不合法/非站点行"""
    if len(row) < 8:
        return False
    station_name = clean_name(row[2])
    if not station_name:
        return False
    if station_name in BAD_STATION_NAMES:
        return False
    # 过滤 '... Stations' 这类集合项
    if station_name.lower().endswith(" stations"):
        return False
    return True


def build_graph_from_london_data(london_tube_data: List[List[str]]) -> Tuple[List[dict], List[dict], Dict[str, Dict[str, float]]]:
    if not london_tube_data or len(london_tube_data) < 2:
        raise ValueError("london_tube_data is empty")

    header = london_tube_data[0]
    rows = london_tube_data[1:]

    # line -> station_id sequence (preserve order)
    line_seq: Dict[str, List[str]] = defaultdict(list)

    # station_id -> info (merge same-name stations)
    station_info: Dict[str, dict] = {}

    for r in rows:
        if not is_valid_row(r):
            continue

        line_name = clean_name(r[0])
        line_color = clean_name(r[1])
        station_name = clean_name(r[2])
        fare_zones = clean_name(r[3])
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
                "fare_zones": set(),
                "station_status": set(),
                "transfer_station": set(),
                "accessible": set(),
                "remarks": set(),
            }

        station_info[sid]["lines"].add(line_name)
        if fare_zones: station_info[sid]["fare_zones"].add(fare_zones)
        if station_status: station_info[sid]["station_status"].add(station_status)
        if transfer_station: station_info[sid]["transfer_station"].add(transfer_station)
        if accessible: station_info[sid]["accessible"].add(accessible)
        if remarks: station_info[sid]["remarks"].add(remarks)

        # 按你提供的顺序连边（避免相邻重复）
        if not line_seq[line_name] or line_seq[line_name][-1] != sid:
            line_seq[line_name].append(sid)

    # edges
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

    # adjacency
    adj: Dict[str, Dict[str, float]] = defaultdict(dict)
    for e in edges:
        a, b, w = e["from_station_id"], e["to_station_id"], float(e["weight"])
        adj[a][b] = min(adj[a].get(b, w), w)
        if e.get("bidirectional", 1):
            adj[b][a] = min(adj[b].get(a, w), w)

    # stations rows
    stations: List[dict] = []
    for s in station_info.values():
        stations.append({
            "station_id": s["station_id"],
            "station_name": s["station_name"],
            "lines": "|".join(sorted(s["lines"])),
            "fare_zones": "|".join(sorted(s["fare_zones"])) if s["fare_zones"] else "",
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
    stations, edges, adj = build_graph_from_london_data(london_tube_data)

    write_csv(
        "london_tube_stations.csv",
        stations,
        ["station_id", "station_name", "lines", "fare_zones", "station_status", "transfer_station", "accessible", "remarks"],
    )
    write_csv(
        "london_tube_edges.csv",
        edges,
        ["from_station_id", "to_station_id", "line_name", "weight", "bidirectional"],
    )
    with open("london_tube_adjacency.json", "w", encoding="utf-8") as f:
        json.dump(adj, f, ensure_ascii=False)

    print(f"OK: stations={len(stations)}, edges={len(edges)}")
    print("Wrote: london_tube_stations.csv, london_tube_edges.csv, london_tube_adjacency.json")


if __name__ == "__main__":
    main()
