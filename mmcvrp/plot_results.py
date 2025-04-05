import json
import matplotlib.pyplot as plt
import os
import sys

methods = ["Bound", "No_Bound"]
comparisons = {"CP": [(14,True),(226,True),(12,True),(220,True),(206,True),(322,True),(167,True),
                      (186,True),(436,True),(244,True), (304,False), (346, True), (434,False),
                      (589,False),(567,False),(286,True),(932,False),(456,False),(334,True),
                      (902,False),(374,False)],
                "SAT": [(14,True),(226,True),(12,True),(220,True),(206,True),(322,True),(167,True),
                      (186,True),(436,True),(244,True),(None,False),(None,False),(1062,False),
                      (None,False),(None,False),(438,False),(None,False),(None,False),(None,False),
                      (None,False),(None,False)],
                "SMT": [(14,True),(226,True),(12,True),(220,True),(206,True),(322,True),(167,True),
                      (186,True),(436,True),(244,True),(547,False),(435,False),(632,False),
                      (1177,False),(1140,False),(286,False),(1525,False),(917,False),(398,False),
                      (1378,False),(648,False)],
                "MIP": [(14,True),(226,True),(12,True),(220,True),(206,True),(322,True),(167,True),
                      (186,True),(436,True),(244,True),(537,False),(346,False),(398,False),
                      (None,False),(838,False),(286,True),(None,False),(568,False),(334,False),
                      (None,False),(548,False)]}

def init_dict():
    d = {}
    for m in methods:
        d[m] = {0.0 : 0}
    for c in comparisons:
        d[c] = {0.0 : 0}
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
    for c in comparisons:
        x_vals = list(d[c].keys())
        y_vals = list(d[c].values())
        plt.plot(x_vals, y_vals, marker='o', label=c)

    plt.xlabel("Instances")
    plt.ylabel("Coverage")
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.savefig(f"{dir}/{filename}")
    plt.close()

def plot_solutions():
    cumulative_coverage = init_dict()
    mean_primal_gap = {}
    for m in methods:
        mean_primal_gap[m] = 0.0
    for c in comparisons:
        mean_primal_gap[c] = 0.0
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
            for c in comparisons:
                coverage = 1 if comparisons[c][i-1][1] else 0
                cost = comparisons[c][i-1][0]
                costs[c] = cost
                if cost is not None and cost < best_known:
                    best_known = cost
                cumulative_coverage[c][i] = cumulative_coverage[c][(i-1)] + coverage
            for m in methods:
                mean_primal_gap[m] += primal_gap(costs[m], best_known)/21 
            for c in comparisons:
                mean_primal_gap[c] += primal_gap(costs[c], best_known)/21        
    save_solutions(cumulative_coverage, title = f"Coverages of different models", 
                   filename=f"Coverage.jpg")
    with open(f"Plots/Primal_gaps.json", "w") as json_file:
                json.dump(mean_primal_gap, json_file, indent=4)
        
if __name__ == "__main__":
    plot_solutions()