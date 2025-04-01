import json
import matplotlib.pyplot as plt
import os

benchmarks = {"C1": 9, "C2": 8, "R1": 12, "R2": 11, "RC1": 8, "RC2": 8}
methods = ["DIDP_Complete", "DIDP_No_Resource", "DIDP_No_Bound","DIDP_Base", "CP"]

def init_dict():
    d = {}
    for m in methods:
        d[m] = {0.0 : 0.0}
    return d


def save_solutions(d, title, filename, vehicle):
    dir = "Plots"
    if vehicle:
        dir="Plots_Vehicles"
    os.makedirs(dir, exist_ok=True)
    plt.figure(figsize=(8, 5))
    for m in methods:
        x_vals = list(d[m].values())
        y_vals = list(d[m].keys())
        plt.plot(x_vals, y_vals, marker='o', label=m)
    
    plt.xlabel("Primal Integral")
    plt.ylabel("Instances")
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.savefig(f"{dir}/{filename}")
    plt.close()

def plot_solutions(vehicle=True):
    all_benchmarks = init_dict()
    all_total = sum(benchmarks.values())
    all_count = 1
    for benchmark in benchmarks:
        cumulative_integral = init_dict()
        total = benchmarks[benchmark]
        for i in range(1, total+1):
            with open(f"Results/{benchmark}/{benchmark}{i:02}.json", "r") as file:
                data = json.load(file)
                for m in methods:
                    p_integral = data[m]["Primal Integral: "]
                    if vehicle:
                        v_used = data[m]["Used Vehicles: "]
                        p_integral = p_integral*v_used
                    cumulative_integral[m][i/total] = cumulative_integral[m][(i-1)/total] + p_integral
                    all_benchmarks[m][all_count/all_total] = all_benchmarks[m][(all_count-1)/all_total] + p_integral
                all_count += 1
        save_solutions(cumulative_integral, title = f"Primal Integral for {benchmark} benchmark instances", 
                       filename=f"{benchmark}.pdf", vehicle=vehicle)
    save_solutions(all_benchmarks, "Primal Integral on all benchmark instances", "Total.pdf",vehicle)
        

if __name__ == "__main__":
    plot_solutions()
        
                
                

