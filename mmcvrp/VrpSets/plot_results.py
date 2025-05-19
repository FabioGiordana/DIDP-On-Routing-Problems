import json
import matplotlib.pyplot as plt
import os
import sys
from pathlib import Path
from utils import primal_gap, primal_integral

methods = ["DIDP_Complete",
           "DIDP_No_Bound",
           "DIDP_No_Implied",
           "DIDP_Base",
           "CP_Model",
           "DIDP_No_Implied_Opt",
           "DIDP_Base_Opt"]

results = ["A", "M", "Golden"]
                

def init_dict():
    d = {}
    for m in methods:
        d[m] = {0.0 : 0.0}
    return d


def save_solutions(d, title, x_title, filename):
    dir = "Plots"
    os.makedirs(dir, exist_ok=True)
    plt.figure(figsize=(8, 5))
    for m in methods:
        x_vals = list(d[m].values())
        y_vals = list(d[m].keys())
        plt.plot(x_vals, y_vals, marker='o', label=m)
    
    plt.xlabel(x_title)
    plt.ylabel("Ratio of Instances")
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.savefig(f"{dir}/{filename}")
    plt.close()
    

    
def best_solution(filename):
    with open(f"{filename}.json", "r") as file:
        data = json.load(file)
        best_known = sys.maxsize
        for m in methods:
            cost = data[m]["Best Cost: "]
            if cost is not None and cost < best_known:
                best_known = cost
    if best_known == sys.maxsize:
        print(f"No solution found for {filename}")
    return best_known

def retrieve_info(filename, method):
    with open(f"{filename}.json", "r") as file:
        data = json.load(file)
        return data[method]["Solution Costs: "], data[method]["Times: "]

def plot_solutions():
    os.makedirs("Plots", exist_ok=True)
    all_integral = init_dict()
    all_gap = init_dict()
    all_count = 1
    all_total = 0
    for g in results:
        folder = f"Results/{g}"
        instances = Path(folder).rglob("*.json")
        instances = list(instances)
        all_total += len(instances)
    for g in results:
        cumulative_integral = init_dict()
        cumulative_gap = init_dict()
        folder = f"Results/{g}"
        instances = Path(folder).rglob("*.json")
        instances = list(instances)
        total = len(instances)
        count = 1
        for filepath in instances:
            filepath = str(filepath.stem)
            best_known = best_solution(f"Results/{g}/{filepath}")
            for m in methods:
                solutions, times = retrieve_info(f"Results/{g}/{filepath}", m)
                if solutions is None:
                    solutions = [None]
                integral = primal_integral(times, solutions, best_known)
                gap = primal_gap(solutions[-1], best_known)
                cumulative_integral[m][count/total] = cumulative_integral[m][(count-1)/total] + integral
                all_integral[m][all_count/all_total] = all_integral[m][(all_count-1)/all_total] + integral
                cumulative_gap[m][count/total] = cumulative_gap[m][(count-1)/total] + gap 
                all_gap[m][all_count/all_total] = all_gap[m][(all_count-1)/all_total] + gap
            count += 1
            all_count += 1

        save_solutions(cumulative_integral, f"Primal Integral for {g} benchmark instances", 
                       "Primal integral", f"Integral_{g}.jpg")
        save_solutions(cumulative_gap, f"Primal Gap for {g} benchmark instances", 
                       "Primal gap", f"Gap_{g}.jpg")
    save_solutions(all_integral, f"Primal Integral for all the benchmark instances", 
                       "Primal integral", f"Integral_Total.jpg")
    save_solutions(all_gap, f"Primal Gap for all the benchmark instances", 
                       "Primal gap", f"Gap_Total.jpg")
    



        
if __name__ == "__main__":
    plot_solutions()