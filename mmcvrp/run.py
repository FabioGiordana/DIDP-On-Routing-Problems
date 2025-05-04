from didp_model import DIDPModel
import os
import json

def read_instances(filename):
    instance = []
    file = open(filename)
    l = 0
    distances = []
    for line in file.readlines():
        line = line.strip()
        if l < 2:
            instance.append(int(line))
        elif l < 4:
            tmp = []
            for part in line.split():
                tmp.append(int(part))
            instance.append(tmp)
        else:
            tmp = []
            for part in line.split(" "):
                tmp.append(int(part))
            distances.append(tmp)
        l += 1
    instance.append(distances)
    return instance


if __name__ == "__main__":
    time_limit = 300
    didp_model = DIDPModel()
    os.makedirs("Results", exist_ok=True)
    for i in range(1, 22):
        instance = read_instances(f"Instances/inst{i:02}.dat")
        if not os.path.exists(f"Results/inst{i:02}.json"):
            print(f"Solving instance {i} with bound")
            data = {} 
            solution_costs, times, solution_path, opt = didp_model.solve(instance,time_limit, bound=True)
            data["Bound"] = {"Times: ": time_used,
                    "Solution Costs: ": solution_cost, 
                    "Optimality: ": opt,
                    "Best Path: ": solution_path}
            print(f"Solving instance {i} with no bound")
            solution_cost, solution_path, opt, time_used = didp_model.solve(instance,time_limit, bound=False)
            data["No_Bound"] = {"Path: ": solution_path,
                    "Solution Cost: ": solution_cost, 
                    "Optimal: ": opt,
                    "Time: ": time_used}
            with open(f"Results/inst{i:02}.json", "w") as json_file:
                json.dump(data, json_file, indent=4)
           