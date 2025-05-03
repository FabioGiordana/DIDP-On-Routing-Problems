from didp_model import DIDPModel
from cp_model import CPModel
import os
import json
import math
import copy
from pathlib import Path
import re

methods = {"DIDP_Complete": (True, True),
           "DIDP_No_Bound": (False, True),
           "DIDP_No_Implied": (True, False),
           "DIDP_Base": (False, False)}

def compute_distance(p1, p2):
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def read_instances(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    metadata = {}
    n = None
    m = None
    q = None
    d = []
    c = []
    node_coords = []

    section = None

    for line in lines:
        line = line.strip()
        if not line or line == "EOF":
            continue

        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
            continue

        if line == "NODE_COORD_SECTION":
            section = "NODE_COORD"
            continue
        elif line == "DEMAND_SECTION":
            section = "DEMAND"
            continue
        elif line == "DEPOT_SECTION":
            section = "DEPOT"
            continue

        if section == "NODE_COORD":
            parts = line.split()
            x = int(parts[1])
            y = int(parts[2])
            node_coords.append((x, y))

        elif section == "DEMAND":
            parts = line.split()
            demand = int(parts[1])
            d.append(demand)

        elif section == "DEPOT":
            if int(line) != -1:
                depot = int(line)
                if depot != 1:
                    print("WRONG DEPOT")
    for i in range(len(node_coords)):
        partial = []
        for j in range(len(node_coords)):
            partial.append(compute_distance(node_coords[i], node_coords[j]))
        c.append(partial)

    # Extract specific structured metadata
    n = int(metadata.get("DIMENSION", len(node_coords)))
    q = int(metadata.get("CAPACITY", 0))

    # Try to infer number of vehicles from the NAME, e.g., X-n101-k25 → 25 vehicles
    name = metadata.get("NAME", "")
    vehicle_match = re.search(r'k(\d+)', name.lower())
    m = int(vehicle_match.group(1)) if vehicle_match else None
    return {
        "n": n,
        "m": m,
        "q": q,
        "d": d,
        "c": c
    }


if __name__ == "__main__":
    time_limit = 600
    folder = "Vrp-Set-A/A"
    cp_model = CPModel()
    didp_model = DIDPModel()
    os.makedirs("Results", exist_ok=True)
    instances = Path(folder).rglob("*.vrp")
    for filepath in instances:
        filepath = str(filepath.stem)
        instance = read_instances(f"{folder}/{filepath}.vrp")
        if instance["n"] > 100:
            print(f"Skipping {filepath} due to the dimension of the instance")
        else:
            dir = f"Results/A"
            os.makedirs(dir, exist_ok=True)
            if os.path.exists(f"{dir}/{filepath}.json"):
                try:
                    with open(f"{dir}/{filepath}.json", "r") as json_file:
                        data = json.load(json_file) 
                except (json.JSONDecodeError, FileNotFoundError):  
                    data = {} 
            else:
                data = {}
            print(f"Solving instance {filepath}")
            if "CP_Model" not in data.keys():
                    print(f"Running CP_Model")
                    solution_cost, solution_path, opt, time_used = cp_model.solve(copy.deepcopy(instance), f"{filepath}", time_limit)
                    data["CP_Model"] = {"Solution Cost: ": solution_cost, 
                    "Path: ": solution_path,
                    "Optimal: ": opt,
                    "Time: ": time_used}
                    with open(f"{dir}/{filepath}.json", "w") as json_file:
                            json.dump(data, json_file, indent=4)
            for method in methods.keys():
                if method not in data.keys():
                    print(f"Running {method}")
                    bound, implied = methods[method]
                    solution_cost, solution_path, opt, time_used = didp_model.solve(instance,time_limit, bound, implied)
                    data[method] = {"Solution Cost: ": solution_cost, 
                    "Path: ": solution_path,
                    "Optimal: ": opt,
                    "Time: ": time_used}
                    with open(f"{dir}/{filepath}.json", "w") as json_file:
                            json.dump(data, json_file, indent=4)