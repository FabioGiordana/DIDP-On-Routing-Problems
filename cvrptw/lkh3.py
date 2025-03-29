from utils import *
import subprocess
import os
import sys

class LKHModel():
    def __init__(self, solver="LKH-3.exe"):
        self.solver = solver

    def make_int(self, array):
        res = []
        for elem in array:
            res.append(int(elem*10))
        return res
    
    def generate_vrptw_file(self, instance, filename, name):
        n = instance["n"]  # Number of nodes
        m = instance["m"]
        q = instance["q"]  # Vehicle capacity
        c = instance["c"]  # Cost matrix (n x n)
        int_c = []
        for row in instance["c"]:
            int_c.append(self.make_int(row))
        d = instance["d"]  # Demand for each node
        ready_time = self.make_int(instance["ready_time"])  # Ready time for each node
        deadline = self.make_int(instance["deadline"])  # Deadline for each node
        service = self.make_int(instance["service"])  # Service time for each node
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write(f"NAME :{name}\n")
            f.write("TYPE : CVRPTW\n")
            f.write(f"DIMENSION : {n}\n")
            f.write(f"VEHICLES : {m}\n")
            f.write(f"CAPACITY : {q}\n")
            f.write("EDGE_WEIGHT_TYPE : EXPLICIT\n")  # Use explicit cost matrix
            f.write("EDGE_WEIGHT_FORMAT : FULL_MATRIX\n")
            f.write("EDGE_WEIGHT_SECTION\n")

            # Write cost matrix
            for row in int_c:
                f.write(" ".join(map(str, row)) + "\n")

            f.write("DEMAND_SECTION\n")
            for i, demand in enumerate(d, start=1):
                f.write(f"{i} {demand}\n")

            f.write("TIME_WINDOW_SECTION\n")
            for i, (rt, dl) in enumerate(zip(ready_time, deadline), start=1):
                f.write(f"{i} {rt} {dl}\n")

            f.write("SERVICE_TIME_SECTION\n")
            for i, s_time in enumerate(service, start=1):
                f.write(f"{i} {s_time}\n")

            f.write("DEPOT_SECTION\n1\n-1\n")  # Assuming node 1 is the depot
            f.write("EOF\n")
    
    def generate_par_file(self, filename, time_limit, vrptw_filename, sol_name):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        os.makedirs(os.path.dirname(sol_name), exist_ok=True)
        with open(filename, "w") as f:
            f.write(f"PROBLEM_FILE = {vrptw_filename}\n")
            f.write(f"TIME_LIMIT = {time_limit}\n") 
            f.write(f"RUNS = 1\n")
            f.write(f"MTSP_SOLUTION_FILE = {sol_name}\n")
            f.write(f"MAX_TRIALS = 1000000000\n")
            

    def solve(self, instance, name, time_limit):
        vrptw_filename = f"LKH-Data/{name}.vrptw"
        par_filename = f"LKH-Data/{name}.par"
        sol_name = f"LKH-Solutions/{name}.sol"
        self.generate_vrptw_file(instance, vrptw_filename, name)
        self.generate_par_file(par_filename, time_limit, vrptw_filename, sol_name)
        try:
            subprocess.run([self.solver, par_filename], capture_output=True, text=True)
        except Exception as e:
            print(f"Error running LKH-3: {e}")
