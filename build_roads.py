import json

# Comprehensive road network covering Royapuram, North Chennai
# Each road has realistic waypoints, widths, capacities, and connections.
roads = [
    # 1. Primary Arterials & Highways
    {
        "id": "beach_road",
        "name": "Kamarajar Salai / Beach Rd",
        "type": "highway",
        "width": 7.5, "lanes": 4, "traffic": 88, "capacity": 2400, "busRoute": True,
        "color": "#27272a", "lineColor": "#facc15",
        "pts": [[13.1120, 80.2988], [13.1090, 80.2983], [13.1065, 80.2977], [13.1040, 80.2971], [13.1015, 80.2965], [13.0980, 80.2958], [13.0950, 80.2952]]
    },
    {
        "id": "royapuram_main",
        "name": "Surya Narayana Salai (Main Rd)",
        "type": "arterial",
        "width": 6.0, "lanes": 2, "traffic": 80, "capacity": 1500, "busRoute": True,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1052, 80.2850], [13.1049, 80.2875], [13.1045, 80.2900], [13.1042, 80.2925], [13.1040, 80.2945], [13.1037, 80.2968], [13.1035, 80.2980]]
    },
    {
        "id": "mc_road",
        "name": "M.C. Road (Mint-Cutchery Rd)",
        "type": "arterial",
        "width": 5.4, "lanes": 2, "traffic": 84, "capacity": 1300, "busRoute": True,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1078, 80.2860], [13.1072, 80.2885], [13.1067, 80.2905], [13.1061, 80.2925], [13.1056, 80.2948]]
    },
    {
        "id": "ga_road",
        "name": "G.A. Road (Washermanpet Link)",
        "type": "arterial",
        "width": 5.2, "lanes": 2, "traffic": 78, "capacity": 1200, "busRoute": True,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1095, 80.2850], [13.1085, 80.2868], [13.1072, 80.2885], [13.1056, 80.2880]]
    },

    # 2. Commercial & Collector Spines
    {
        "id": "ms_koil",
        "name": "M.S. Koil Street (Bazaar)",
        "type": "commercial",
        "width": 4.5, "lanes": 2, "traffic": 90, "capacity": 700, "busRoute": False,
        "color": "#27272a", "lineColor": "#facc15",
        "pts": [[13.1058, 80.2908], [13.1053, 80.2922], [13.1048, 80.2934], [13.1045, 80.2946], [13.1041, 80.2958]]
    },
    {
        "id": "west_madha",
        "name": "West Madha Church St",
        "type": "connector",
        "width": 4.2, "lanes": 2, "traffic": 68, "capacity": 750, "busRoute": False,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1082, 80.2900], [13.1065, 80.2905], [13.1046, 80.2910], [13.1030, 80.2915], [13.1012, 80.2918]]
    },
    {
        "id": "east_madha",
        "name": "East Madha Church St",
        "type": "connector",
        "width": 4.2, "lanes": 2, "traffic": 65, "capacity": 700, "busRoute": False,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1085, 80.2936], [13.1068, 80.2938], [13.1050, 80.2941], [13.1034, 80.2943], [13.1018, 80.2947]]
    },
    {
        "id": "kalmandapam",
        "name": "Kalmandapam Road",
        "type": "connector",
        "width": 4.0, "lanes": 2, "traffic": 58, "capacity": 600, "busRoute": False,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1076, 80.2946], [13.1062, 80.2952], [13.1051, 80.2958], [13.1039, 80.2964], [13.1025, 80.2968]]
    },
    {
        "id": "pv_kovil",
        "name": "P.V. Kovil Street",
        "type": "connector",
        "width": 3.8, "lanes": 2, "traffic": 54, "capacity": 550, "busRoute": False,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1070, 80.2870], [13.1056, 80.2875], [13.1044, 80.2878], [13.1032, 80.2882], [13.1018, 80.2885]]
    },
    {
        "id": "bc_press",
        "name": "BC Press Road (Hospital Rd)",
        "type": "connector",
        "width": 4.4, "lanes": 2, "traffic": 64, "capacity": 650, "busRoute": False,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1018, 80.2868], [13.1023, 80.2890], [13.1027, 80.2912], [13.1030, 80.2935], [13.1032, 80.2955]]
    },
    {
        "id": "srm_road",
        "name": "SRM Road (Coastal Access)",
        "type": "connector",
        "width": 4.6, "lanes": 2, "traffic": 60, "capacity": 700, "busRoute": True,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1092, 80.2920], [13.1084, 80.2938], [13.1078, 80.2954], [13.1072, 80.2968], [13.1066, 80.2982]]
    },

    # 3. Harbour & Station Special Access Corridors
    {
        "id": "harbour_link",
        "name": "Kasimedu Harbour Wharf Rd",
        "type": "connector",
        "width": 5.2, "lanes": 2, "traffic": 76, "capacity": 900, "busRoute": True,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1082, 80.2952], [13.1098, 80.2958], [13.1112, 80.2965], [13.1128, 80.2972], [13.1135, 80.2980]]
    },
    {
        "id": "harbour_coastal_lane",
        "name": "Kasimedu Fish Market Lane",
        "type": "residential",
        "width": 3.4, "lanes": 1, "traffic": 50, "capacity": 400, "busRoute": False,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1128, 80.2972], [13.1118, 80.2955], [13.1105, 80.2942], [13.1092, 80.2920]]
    },
    {
        "id": "station_approach",
        "name": "Station Approach Road",
        "type": "connector",
        "width": 4.5, "lanes": 2, "traffic": 72, "capacity": 700, "busRoute": False,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1065, 80.2922], [13.1067, 80.2912], [13.1069, 80.2898], [13.1072, 80.2885]]
    },
    {
        "id": "station_goods_shed",
        "name": "Old Goods Shed Lane",
        "type": "residential",
        "width": 3.2, "lanes": 1, "traffic": 40, "capacity": 350, "busRoute": False,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1065, 80.2922], [13.1058, 80.2928], [13.1050, 80.2932], [13.1042, 80.2925]]
    },
    {
        "id": "stanley_subway",
        "name": "Stanley Subway Underpass",
        "type": "connector",
        "width": 4.6, "lanes": 2, "traffic": 78, "capacity": 850, "busRoute": True,
        "color": "#27272a", "lineColor": "#facc15",
        "pts": [[13.1012, 80.2860], [13.0995, 80.2872], [13.0980, 80.2885], [13.0965, 80.2892]]
    },
    {
        "id": "hospital_ring",
        "name": "Stanley Hospital Ring Rd",
        "type": "connector",
        "width": 4.0, "lanes": 2, "traffic": 65, "capacity": 600, "busRoute": False,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.0995, 80.2872], [13.0990, 80.2862], [13.1002, 80.2855], [13.1012, 80.2860]]
    },
    {
        "id": "metro_feeder",
        "name": "Mannadi Metro Feeder Way",
        "type": "connector",
        "width": 4.6, "lanes": 2, "traffic": 82, "capacity": 1000, "busRoute": True,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.0980, 80.2885], [13.0970, 80.2868], [13.0960, 80.2850], [13.0950, 80.2842]]
    },

    # 4. Dense Residential Cross Streets & Alleys
    {
        "id": "grace_garden_main",
        "name": "Grace Garden Main Road",
        "type": "residential",
        "width": 3.6, "lanes": 1, "traffic": 45, "capacity": 450, "busRoute": False,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1088, 80.2885], [13.1078, 80.2892], [13.1067, 80.2905], [13.1055, 80.2915]]
    },
    {
        "id": "grace_cross_1",
        "name": "Grace Garden 1st Lane",
        "type": "residential",
        "width": 3.0, "lanes": 1, "traffic": 35, "capacity": 300, "busRoute": False,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1082, 80.2875], [13.1076, 80.2890], [13.1070, 80.2902]]
    },
    {
        "id": "grace_cross_2",
        "name": "Grace Garden 2nd Lane",
        "type": "residential",
        "width": 3.0, "lanes": 1, "traffic": 32, "capacity": 300, "busRoute": False,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1074, 80.2880], [13.1068, 80.2895], [13.1062, 80.2910]]
    },
    {
        "id": "pudumanaikuppam_st",
        "name": "Pudumanaikuppam Street",
        "type": "residential",
        "width": 3.4, "lanes": 1, "traffic": 42, "capacity": 380, "busRoute": False,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1066, 80.2905], [13.1062, 80.2922], [13.1058, 80.2938], [13.1054, 80.2952]]
    },
    {
        "id": "st_anthony_lane",
        "name": "St. Anthony Cross Lane",
        "type": "residential",
        "width": 3.0, "lanes": 1, "traffic": 36, "capacity": 320, "busRoute": False,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1032, 80.2915], [13.1030, 80.2932], [13.1028, 80.2948], [13.1026, 80.2965]]
    },
    {
        "id": "st_peters_lane",
        "name": "St. Peter's Church Lane",
        "type": "residential",
        "width": 3.2, "lanes": 1, "traffic": 38, "capacity": 350, "busRoute": False,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1038, 80.2940], [13.1030, 80.2945], [13.1022, 80.2952]]
    },
    {
        "id": "amman_temple_lane",
        "name": "Angalamman Koil Lane",
        "type": "residential",
        "width": 3.2, "lanes": 1, "traffic": 48, "capacity": 360, "busRoute": False,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1060, 80.2900], [13.1055, 80.2910], [13.1050, 80.2920]]
    },
    {
        "id": "subramania_lane",
        "name": "Subramania Swamy Lane",
        "type": "residential",
        "width": 3.2, "lanes": 1, "traffic": 46, "capacity": 360, "busRoute": False,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1042, 80.2915], [13.1038, 80.2925], [13.1034, 80.2935]]
    },
    {
        "id": "fire_temple_lane",
        "name": "Parsi Agiary Lane",
        "type": "residential",
        "width": 3.0, "lanes": 1, "traffic": 28, "capacity": 280, "busRoute": False,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1050, 80.2930], [13.1045, 80.2935], [13.1040, 80.2942]]
    },
    {
        "id": "theagaraya_lane",
        "name": "Sir Theagaraya College Lane",
        "type": "residential",
        "width": 3.4, "lanes": 1, "traffic": 44, "capacity": 380, "busRoute": False,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1020, 80.2878], [13.1010, 80.2880], [13.1002, 80.2885]]
    },
    {
        "id": "port_boundary_road",
        "name": "Chennai Port Boundary Road",
        "type": "connector",
        "width": 4.8, "lanes": 2, "traffic": 70, "capacity": 850, "busRoute": True,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1035, 80.2980], [13.1010, 80.2975], [13.0985, 80.2968], [13.0960, 80.2960]]
    },
    {
        "id": "singara_garden_st",
        "name": "Singara Garden Street",
        "type": "residential",
        "width": 3.2, "lanes": 1, "traffic": 34, "capacity": 320, "busRoute": False,
        "color": "#27272a", "lineColor": "#ffffff",
        "pts": [[13.1068, 80.2885], [13.1060, 80.2895], [13.1052, 80.2905]]
    }
]

out_path = "c:/Users/SAAQIB/areatwin/royapuram_roads.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(roads, f, indent=2)

print(f"Generated {len(roads)} comprehensive Royapuram roads and lanes in {out_path}!")
