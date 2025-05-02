from didp_model import DIDPModel
from cp_model import CPModel
import os
import json
import math
import copy

methods = {"DIDP_Complete": (True, True),
           "DIDP_No_Bound": (False, True),
           "DIDP_No_Implied": (True, False),
           "DIDP_Base": (False, False)}

benchmarks = {"C1": 9, "C2": 8, "R1": 12, "R2": 11, "RC1": 8, "RC2": 8}

def compute_distance(p1, p2):
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def read_instances(file_path):
    m = None
    a = []
    b = []
    c = []
    q = None
    d = []
    s = []
    positions = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
    section = None  # To track where we are in the file
    for line in lines:
        line = line.strip()
        if not line:
            continue  # Skip empty lines
        # Identify sections
        if "VEHICLE" in line:
            section = "vehicle"
            continue
        elif "CUSTOMER" in line:
            section = "customer"
            continue
        # Read vehicle information
        if section == "vehicle":
            if "NUMBER" in line:  # Skip headers
                continue
            parts = line.split()
            if len(parts) == 2:
                m = int(parts[0])
                q = int(parts[1])
        # Read customer data
        elif section == "customer":
            if "CUST NO." in line:  # Skip headers
                continue
            parts = line.split()
            if len(parts) == 7:  # Ensure correct data row
                positions.append((int(parts[1]), int(parts[2])))
                d.append(int(parts[3]))
                a.append(int(parts[4]))
                b.append(int(parts[5]))
                s.append(int(parts[6]))
    for i in range(len(positions)):
        partial = []
        for j in range(len(positions)):
            partial.append(compute_distance(positions[i], positions[j]))
        c.append(partial)
    return{
        "n": len(c),
        "m": m,
        "q": q,
        "d": d,
        "c": c,
        "ready_time": a,
        "deadline": b,
        "service": s
    }

if __name__ == "__main__":
    time_limit = 600
    cp_model = CPModel()
    didp_model = DIDPModel()
    os.makedirs("Results", exist_ok=True)
    for benchmark in benchmarks.keys():
        number = benchmarks[benchmark]
        dir = f"Results/{benchmark}"
        os.makedirs(dir, exist_ok=True)
        for i in range(1, number+1):
            instance = read_instances(f"Vrp-Set-Solomon/{benchmark}{i:02}.txt")
            if os.path.exists(f"{dir}/{benchmark}{i:02}.json"):
                try:
                    with open(f"{dir}/{benchmark}{i:02}.json", "r") as json_file:
                        data = json.load(json_file) 
                except (json.JSONDecodeError, FileNotFoundError):  
                    data = {} 
            else:
                data = {}
            print(f"Solving instance {benchmark}{i:02}")
            for method in methods.keys():
                if "CP_Model" not in data.keys():
                    print(f"Running CP_Model")
                    solution_cost, solution_path, opt, time_used = cp_model.solve(copy.deepcopy(instance), f"{benchmark}{i:02}", time_limit)
                    data["CP_Model"] = {"Solution Cost: ": solution_cost, 
                    "Path: ": solution_path,
                    "Optimal: ": opt,
                    "Time: ": time_used}
                    with open(f"{dir}/{benchmark}{i:02}.json", "w") as json_file:
                            json.dump(data, json_file, indent=4)
                if method not in data.keys():
                    print(f"Running {method}")
                    bound, implied = methods[method]
                    solution_cost, solution_path, opt, time_used = didp_model.solve(instance,time_limit, bound, implied)
                    data[method] = {"Solution Cost: ": solution_cost, 
                    "Path: ": solution_path,
                    "Optimal: ": opt,
                    "Time: ": time_used}
                    with open(f"{dir}/{benchmark}{i:02}.json", "w") as json_file:
                            json.dump(data, json_file, indent=4)