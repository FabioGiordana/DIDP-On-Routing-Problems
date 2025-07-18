from didp_model import DIDPModel
from cp_model import CPModel
import os
import json
import math
import copy
from pathlib import Path
import re

methods = {"DIDP_Complete": (True, True, False, False),
           "DIDP_No_Bound": (False, True, False, False),
           "DIDP_No_Implied": (True, False, False, False),
           "DIDP_Base": (False, False, False, False),
           "DIDP_No_Implied_Opt": (True, False, True, False),
           "DIDP_Base_Opt": (False, False, True, False),
           "DIDP_GTR_Complete": (True, True, False, True),
           "DIDP_GTR_No_Bound": (False, True, False, True),
           "DIDP_GTR_No_Implied": (True, False, False, True),
           "DIDP_GTR_Base": (False, False, False, True)}

def compute_distance(p1, p2):
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def count_vehicles(file_path):
    num_routes = 0
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith("Route #"):
                num_routes += 1
    return num_routes

def read_instances(file_path):
    with open(f"{file_path}.vrp", 'r') as f:
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
            x = float(parts[1])
            y = float(parts[2])
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
    if m is None:
        m = count_vehicles(f"{file_path}.sol")
        
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
        instance = read_instances(f"{folder}/{filepath}")
        if instance["n"] > 501:
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
            for method in ["CP_Model", "CP_Model_No_Imp", "CP_Model_GTR"]:
                if method not in data.keys():
                        print(f"Running {method}")
                        solution_costs, times, best_cost, best_path, opt = cp_model.solve(copy.deepcopy(instance), f"{filepath}", time_limit, method)
                        data[method] = {"Times: ": times,
                        "Solution Costs: ": solution_costs, 
                        "Optimality: ": opt,
                        "Best Cost: ": best_cost,
                        "Best Path: ": best_path}
                        with open(f"{dir}/{filepath}.json", "w") as json_file:
                                json.dump(data, json_file, indent=4)
            for method in methods.keys():
                if method not in data.keys():
                    print(f"Running {method}")
                    bound, implied, opt, gtr = methods[method]
                    solution_costs, times, best_cost, best_path, opt = didp_model.solve(instance,time_limit, bound, implied, opt, gtr)
                    data[method] = {"Times: ": times,
                    "Solution Costs: ": solution_costs, 
                    "Optimality: ": opt,
                    "Best Cost: ": best_cost,
                    "Best Path: ": best_path}
                    with open(f"{dir}/{filepath}.json", "w") as json_file:
                            json.dump(data, json_file, indent=4)
        