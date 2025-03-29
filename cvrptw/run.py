import math
from didp_model import DIDPModel
from cp_model import CPModel
from lkh3 import LKHModel
import json
import os
import copy

methods = {"DIDP_Complete": (True, True),
           "DIDP_No_Resource": (False, True),
           "DIDP_No_Bound": (True, False),
           "DIDP_Base": (False, False)}

benchmarks = {"C1": 9, "C2": 8, "R1": 12, "R2": 11, "RC1": 8, "RC2": 8}
           


def compute_distance(p1, p2):
    x1 = p1[0]
    y1 = p1[1]
    x2 = p2[0]
    y2 = p2[1]
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def extract_best_sol(file_path):
    with open(file_path, "r") as file:  
        lines = file.readlines()
    for line in lines:
        if line.startswith("Cost"):
            cost = float(line.split()[1])  
            return cost

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
    lkh3_solver = LKHModel()
    os.makedirs("Results", exist_ok=True)
    for benchmark in benchmarks.keys():
        number = benchmarks[benchmark]
        dir = f"Results/{benchmark}"
        os.makedirs(dir, exist_ok=True)
        for i in range(1, number+1):
            instance = read_instances(f"Vrp-Set-Solomon/{benchmark}{i:02}.txt")
            best_known = extract_best_sol(f"Vrp-Set-Solomon/{benchmark}{i:02}.sol")
            if os.path.exists(f"{dir}/{benchmark}{i:02}.json"):
                try:
                    with open(f"{dir}/{benchmark}{i:02}.json", "r") as json_file:
                        data = json.load(json_file) 
                except (json.JSONDecodeError, FileNotFoundError):  
                    data = {} 
            else:
                print(f"Solving instance {benchmark}{i:02}")
                data = {} 
                for method in methods.keys():
                    resource, bound = methods[method]
                    vehicles, solution_path, solution_cost, integral, gap = didp_model.solve(instance, best_known, time_limit, resource, bound)
                    data[method] = {"Path: ": solution_path,
                                "Solution Cost: ": solution_cost, 
                                "Used Vehicles: ": vehicles,
                                "Primal Integral: ": integral,
                                "Primal Gap: ": gap}
                vehicles, solution_path, solution_cost, integral, gap = cp_model.solve(copy.deepcopy(instance), best_known, f"{benchmark}{i:02}", time_limit)
                data["CP"] = {"Path: ": solution_path,
                            "Best Solution Cost: ": solution_cost, 
                            "Used Vehicles: ": vehicles,
                                "Primal Integral: ": integral,
                                "Primal Gap: ": gap}
                with open(f"{dir}/{benchmark}{i:02}.json", "w") as json_file:
                    json.dump(data, json_file, indent=4)
            if not os.path.exists(f"LKH-Solutions/{benchmark}{i:02}.sol"):
                print(f"Solving instance {benchmark}{i:02} with lkh")
                lkh3_solver.solve(instance, f"{benchmark}{i:02}", time_limit)
            





