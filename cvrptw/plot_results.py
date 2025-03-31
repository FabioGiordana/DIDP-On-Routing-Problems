import json
import matplotlib.pyplot as plt

benchmarks = {"C1": 9, "C2": 8, "R1": 12, "R2": 11, "RC1": 8, "RC2": 8}
methods = ["DIDP_Complete", "DIDP_No_Resource", "DIDP_No_Bound","DIDP_Base", "CP"]

def init_dict():
    d = {}
    for m in methods:
        d[m] = {0.0 : 0.0}
    return d


def plot_solutions(cumulative_integral):
    plt.figure(figsize=(8, 5))
    for m in methods:
        x_vals = list(cumulative_integral[m].keys())
        y_vals = list(cumulative_integral[m].values())
        plt.plot(x_vals, y_vals, marker='o', label=m)
    
    plt.xlabel("Progress (fraction)")
    plt.ylabel("Cumulative Primal Integral")
    plt.title(f"Benchmark: {benchmark}")
    plt.legend()
    plt.grid()
    plt.show()

def read_solutions(dir = "Results"):
    for benchmark in benchmarks:
        cumulative_integral = init_dict()
        total = benchmarks[benchmark]
        for i in range(1, total+1):
            with open(f"{dir}/{benchmark}/{benchmark}{i:02}.json", "r") as file:
                data = json.load(file)
                for m in methods:
                    p_integral = data[m]["Primal Integral: "]
                    cumulative_integral[m][i/total] = cumulative_integral[m][(i-1)/total] + p_integral
        

if __name__ == "__main__":
    plot_solutions()
        
                
                

