from datetime import timedelta
import os
from minizinc import Solver, Instance, Model, Status
import time

class CPModel():
    def __init__(self, model="mmcvrp.mzn"):
        self.model = model

    def make_int(self, array):
        res = []
        for elem in array:
            res.append(int(elem*1000))
        return res

    def convert_instance(self, instance, cp_instance):
        n = instance["n"]
        m = instance["m"]
        int_c = []
        for row in instance["c"]:
            int_c.append(self.make_int(row))
        min_to_from = [int_c[0][j] + int_c[j][0] for j in range(n)]
        max_to = [max(int_c[j][k] for k in range(n) if k != j) for j in range(n)]
        max_from = [max(int_c[k][j] for k in range(n) if k != j) for j in range(n)]
        cp_instance["n"] = n
        cp_instance["m"] = m
        cp_instance["q"] = instance["q"]
        cp_instance["d"] = instance["d"]
        cp_instance["c"] = int_c
        cp_instance["lower_b"] = max(min_to_from)
        cp_instance["upper_b"] = min(sum(max_to), sum(max_from))

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

  
    def build_paths(self, paths):
        sol = []
        for path in paths:
            tmp = []
            next = path[0] - 1
            while next != 0:
                tmp.append(next)
                next = path[next] - 1
            sol.append(tmp)
        return sol

    def solve(self, instance, name, time_limit):
        filename = f"Minizinc-Data/{name}.dzn"
        self.write_dzn_file(filename, instance)
        solver = Solver.lookup("gecode")
        m = Model(f"mmcvrp.mzn")
        cp_instance = Instance(solver, m)
        self.convert_instance(instance, cp_instance) 
        start_time = time.time()
        result = cp_instance.solve(timeout=timedelta(seconds=time_limit))
        optimal = False
        if result.status is Status.OPTIMAL_SOLUTION:
            optimal = True
        if result.status is Status.UNKNOWN:
            return None, None, None, None
        path = result["path"]
        solution_cost = result["objective"]
        solution_path = self.build_paths(path)
        used_time = time.time() - start_time
        return solution_cost/1000, solution_path, optimal, used_time