import subprocess
import re
from utils import *
import os


class CPModel():
    def __init__(self, model="cvrptw.mzn"):
        self.model = model

    def make_int(self, array):
        res = []
        for elem in array:
            res.append(int(elem*1000))
        return res

    def modify_array(self, arr, n, m):
        res = []
        for i in range(1,n):
            res.append(arr[i])
        for i in range(2*m):
            res.append(arr[0])
        return res

    def modify_cost(self, arr, n, m):
        res = []
        for i in range(1,n):
            tmp = arr[i][1:]
            for _ in range(2*m):
                tmp.append(arr[i][0])
            res.append(tmp)
        for _ in range(2*m):
            tmp = arr[0][1:]
            for _ in range(2*m):
                tmp.append(arr[0][0])
            res.append(tmp)
        return res

    def convert_instance(self, instance):
        n = instance["n"]
        instance["n"] = instance["n"]-1
        m = instance["m"]
        int_c = []
        for row in instance["c"]:
            int_c.append(self.make_int(row))
        min_to = [min(int_c[j][k] for k in range(n) if k != j) for j in range(n)]
        min_from = [min(int_c[k][j] for k in range(n) if k != j) for j in range(n)]
        max_to = [max(int_c[j][k] for k in range(n) if k != j) for j in range(n)]
        max_from = [max(int_c[k][j] for k in range(n) if k != j) for j in range(n)]
        instance["d"] = self.modify_array(instance["d"], n, m)
        instance["c"] = self.modify_cost(int_c, n, m)
        instance["ready_time"] = self.modify_array(self.make_int(instance["ready_time"]), n, m)
        instance["deadline"] = self.modify_array(self.make_int(instance["deadline"]), n, m)
        instance["service"] = self.modify_array(self.make_int(instance["service"]), n, m)
        instance["lower_b"] = max(sum(min_to), sum(min_from))
        instance["upper_b"] = min(sum(max_to), sum(max_from))
        return instance

    def write_dzn_file(self, filename, inst):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            for key, value in inst.items():
                if isinstance(value, list):
                    if all(isinstance(row, list) for row in value):  # 2D array
                        formatted_matrix = " | ".join(", ".join(map(str, row)) for row in value)
                        f.write(f"{key} = [| {formatted_matrix} |];\n")
                    else:  # 1D array
                        f.write(f"{key} = [{', '.join(map(str, value))}];\n")
                elif isinstance(value, str):  # Handle strings
                    f.write(f"{key} = \"{value}\";\n")
                else:  # Handle integers, floats, etc.
                    f.write(f"{key} = {value};\n")

    def extract_obj_time(self, data, n, m,c):
        matches = re.findall(r"pred\s*=\s*\[([^\]]+)\]", data)
        pred = list(map(int, matches[-1].split(',')))  # Get last match & convert to list
        start_nodes = [i for i in range(n+1, n+m+1)]
        end_nodes = [i for i in range(n+m+1, n+2*m+1)]
        customer = pred[-1]
        paths=[]
        path=[]
        vehicles = 0
        while customer != n+1:
            if customer in start_nodes:
                if path:
                    vehicles+=1
                    path.reverse()
                    paths.append(path)
                path = []
            elif customer in end_nodes:
                if path:
                    vehicles+=1
                    path.reverse()
                    paths.append(path)
                path = []
            else:
                path.append(customer)
            customer = pred[customer-1]
        if path:
            vehicles+=1
            path.reverse()
            paths.append(path)        
        paths.reverse()
        cost = 0
        for path in paths:
            cost += c[-1][path[0]-1]
            for i in range(0, len(path)-1):
               cost += c[path[i]-1][path[i+1]-1] 
            cost += c[path[-1]-1][-1]
        # Regular expressions to match obj values and time elapsed
        obj_pattern = re.findall(r'obj\s*=\s*(\d+)', data)
        time_pattern = re.findall(r'% time elapsed:\s*([\d.]+)', data)
        # Convert to appropriate types
        obj_values = list(map(int, obj_pattern))
        time_values = list(map(float, time_pattern))
        return vehicles, paths, obj_values, time_values

    def solve(self, instance, best_known, name, time_limit=300):
        instance = self.convert_instance(instance)
        filename = f"Minizinc-Data/{name}.dzn"
        self.write_dzn_file(filename, instance)
        result = subprocess.run(
            ['minizinc', '--solver', 'gecode', '--output-time', '--fzn-flags', 
             f'--time {time_limit*1000}', self.model, filename],
            capture_output=True, text=True
        )
        vehicles, solution_path, solution_costs, times = self.extract_obj_time(result.stdout, instance["n"], instance["m"], instance["c"])
        solution_costs = [round(s/1000,1) for s in solution_costs]
        solution_costs.insert(0, None)
        times.insert(0, 0)
        times.append(max(times[-1], time_limit))
        return vehicles, solution_path, solution_costs[-1], primal_integral(times, solution_costs, best_known), primal_gap(solution_costs[-1], best_known)


