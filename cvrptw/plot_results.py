import json
import matplotlib.pyplot as plt
import os

benchmarks = {"C1": 9, "C2": 8, "R1": 12, "R2": 11, "RC1": 8, "RC2": 8}
one_group = {"C1": 9, "R1": 12, "RC1": 8}
two_group = {"C2": 8, "R2": 11, "RC2": 8}
c_group = {"C1": 9, "C2": 8}
r_group = {"R1": 12, "R2": 11}
rc_group = {"RC1": 8, "RC2": 8}
groups = {"1-Group": one_group, "2-Group": two_group, "C-Group":c_group, "R-Group":r_group, 
          "RC-Group": rc_group}
methods = ["DIDP_Complete", "DIDP_No_Resource", "DIDP_No_Bound","DIDP_Base", "CP"]

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

def plot_solutions_grouped():
    for g in groups:
        cumulative_integral = init_dict()
        cumulative_gap = init_dict()
        total = sum(groups[g].values())
        count = 1
        for s in groups[g]:
            for i in range(1, groups[g][s]+1):
                with open(f"Results/{s}/{s}{i:02}.json", "r") as file:
                    data = json.load(file)
                    for m in methods:
                        p_integral = data[m]["Primal Integral: "]
                        cumulative_integral[m][count/total] = cumulative_integral[m][(count-1)/total] + p_integral
                        p_gap = data[m]["Primal Gap: "]
                        cumulative_gap[m][count/total] = cumulative_gap[m][(count-1)/total] + p_gap
                count += 1
            save_solutions(cumulative_integral, f"Primal Integral for {g} benchmark instances", 
                       "Primal integral", f"Integral_{g}.jpg")
            save_solutions(cumulative_gap, f"Primal Gap for {g} benchmark instances", 
                       "Primal gap", f"Gap_{g}.jpg")

def plot_solutions():
    all_benchmarks_int = init_dict()
    all_benchmarks_gap = init_dict()
    all_total = sum(benchmarks.values())
    all_count = 1
    for benchmark in benchmarks:
        cumulative_integral = init_dict()
        cumulative_gap = init_dict()
        total = benchmarks[benchmark]
        for i in range(1, total+1):
            with open(f"Results/{benchmark}/{benchmark}{i:02}.json", "r") as file:
                data = json.load(file)
                for m in methods:
                    p_integral = data[m]["Primal Integral: "]
                    cumulative_integral[m][i/total] = cumulative_integral[m][(i-1)/total] + p_integral
                    all_benchmarks_int[m][all_count/all_total] = all_benchmarks_int[m][(all_count-1)/all_total] + p_integral
                    p_gap = data[m]["Primal Gap: "]
                    cumulative_gap[m][i/total] = cumulative_gap[m][(i-1)/total] + p_gap
                    all_benchmarks_gap[m][all_count/all_total] = all_benchmarks_gap[m][(all_count-1)/all_total] + p_gap
                all_count += 1
        save_solutions(cumulative_integral, f"Primal Integral for {benchmark} benchmark instances", 
                       "Primal integral", f"Integral_{benchmark}.jpg")
        save_solutions(cumulative_gap, f"Primal Gap for {benchmark} benchmark instances", 
                       "Primal gap", f"Gap_{benchmark}.jpg")
    save_solutions(all_benchmarks_int, "Primal Integral on all benchmark instances",
                   "Primal integral", "Total_Integral.jpg")
    save_solutions(all_benchmarks_gap, "Primal Gap on all benchmark instances",
                   "Primal gap", "Total_Gap.jpg")
        

if __name__ == "__main__":
    plot_solutions()
    plot_solutions_grouped()
        
                
                

