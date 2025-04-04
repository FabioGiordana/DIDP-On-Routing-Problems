import json
import matplotlib.pyplot as plt
import os
import sys

methods = ["Bound", "No_Bound"]

def init_dict():
    d = {}
    for m in methods:
        d[m] = {0.0 : 0}
    return d

def primal_gap(solution_cost, best_known):
    if solution_cost is None or solution_cost*best_known < 0:
        return 1
    elif solution_cost==best_known==0:
        return 0
    else:
        return abs(solution_cost - best_known)/(max(abs(solution_cost), abs(best_known)))


def save_solutions(d, title, filename):
    dir = "Plots"
    os.makedirs(dir, exist_ok=True)
    plt.figure(figsize=(8, 5))
    for m in methods:
        x_vals = list(d[m].keys())
        y_vals = list(d[m].values())
        plt.plot(x_vals, y_vals, marker='o', label=m)
    
    plt.xlabel("Instances")
    plt.ylabel("Coverage")
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.savefig(f"{dir}/{filename}")
    plt.close()

def plot_solutions():
    cumulative_coverage = init_dict()
    mean_primal_gap = {"Bound": 0.0, "No_Bound": 0.0}
    for i in range(1,22):
        with open(f"Results//inst{i:02}.json", "r") as file:
            data = json.load(file)
            best_known = sys.maxsize
            costs = {}
            for m in methods:
                coverage = 1 if data[m]["Optimal: "] else 0
                cost = data[m]["Solution Cost: "]
                costs[m] = cost
                if cost < best_known:
                    best_known = cost
                cumulative_coverage[m][i] = cumulative_coverage[m][(i-1)] + coverage
            for m in methods:
                mean_primal_gap[m] += primal_gap(costs[m], best_known)/21       
            
    save_solutions(cumulative_coverage, title = f"Coverage", filename=f"Coverage.jpg")
    with open(f"Plots/Primal_gaps.json", "w") as json_file:
                json.dump(mean_primal_gap, json_file, indent=4)
        
if __name__ == "__main__":
    plot_solutions()