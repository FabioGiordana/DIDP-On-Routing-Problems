from utils import check_solution
import os
import subprocess
import re

methods = {"CP_Model": "mmcvrp.mzn",
           "CP_Model_No_Imp": "mmcvrp_no_imp.mzn",
           "CP_Model_GTR" : "mmcvrp_gtr.mzn",
           "CP_Model_GTR_Implied" : "mmcvrp_gtr_imp.mzn"}

class CPModel():
    def __init__(self):
        pass

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
        cp_instance = {}
        n = instance["n"]
        m = instance["m"]
        int_c = []
        for row in instance["c"]:
            int_c.append(self.make_int(row))
        min_to_from = [int_c[0][j] + int_c[j][0] for j in range(n)]
        max_to = [max(int_c[j][k] for k in range(n) if k != j) for j in range(n)]
        max_from = [max(int_c[k][j] for k in range(n) if k != j) for j in range(n)]
        cp_instance["n"] = n - 1
        cp_instance["m"] = m
        cp_instance["q"] = instance["q"]
        cp_instance["d"] = self.modify_array(instance["d"], n, m)
        cp_instance["c"] = self.modify_cost(int_c, n, m)
        cp_instance["lower_b"] = max(min_to_from)
        cp_instance["upper_b"] = min(sum(max_to), sum(max_from))
        return cp_instance

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

  
    def extract_obj_time(self, stdout, instance):
        n = instance["n"] - 1
        m = instance["m"]
        int_c = []
        for row in instance["c"]:
            int_c.append(self.make_int(row))
        instance["c"] = int_c
        # Extract all objective values
        obj_values = list(map(int, re.findall(r'obj\s*=\s*(\d+)', stdout)))
        
        # Extract all elapsed times
        times = list(map(float, re.findall(r'% time elapsed:\s*([\d.]+)\s*s', stdout)))
        
        # Extract the last path array (flattened)
        matches = re.findall(r"path\s*=\s*\[([^\]]+)\]", stdout)
        sol_path = list(map(int, matches[-1].split(',')))  # Get last match & convert to list
        start_nodes = [i for i in range(n+1, n+m+1)]
        end_nodes = [i for i in range(n+m+1, n+2*m+1)]
        if not matches:
            raise ValueError("No path array found in stdout.")
        customer = sol_path[n]
        paths = []
        path = []
        while customer != n + 2*m:
            if customer in end_nodes:
                if len(path) > 0:
                    paths.append(path)
            elif customer in start_nodes:
                path = []
            else:
                path.append(customer)
            customer = sol_path[customer-1]
        if len(path) > 0:
            paths.append(path)

        check_solution(paths, obj_values[-1], instance)
        optimal_match = re.findall(r'={10}(.*)', stdout)
        is_optimal = any("optimal" in line.lower() for line in optimal_match) or len(optimal_match) == 1

        return paths, obj_values, times, is_optimal

    def solve(self, instance, name, time_limit, method):
        cp_instance = self.convert_instance(instance)
        filename = f"Minizinc-Data/{name}.dzn"
        self.write_dzn_file(filename, cp_instance)
        result = subprocess.run(
            ['minizinc', '--solver', 'gecode', "--all-solutions", '--output-time', '--fzn-flags', 
             f'--time {time_limit*1000}', methods[method], filename],
            capture_output=True, text=True
        )
        if "UNKNOWN" in result.stdout:
            solution_costs = None
            times = []
            best_cost = None
            solution_path = None
            opt = False
        else:
            solution_path, solution_costs, times, opt = self.extract_obj_time(result.stdout, instance)
            solution_costs = [round(s/1000,1) for s in solution_costs]
            solution_costs.insert(0, None)
            best_cost = solution_costs[-1]
        times.insert(0, 0)
        times.append(max(times[-1], time_limit))
        return solution_costs, times, best_cost, solution_path, opt