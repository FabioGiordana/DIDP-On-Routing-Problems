import didppy as dp
from utils import *
import re

class DIDPModel():

    def define_model(self, instance, resource=True, bound=True):
        n = instance["n"]
        m = instance["m"]
        q = instance["q"]
        d = instance["d"]
        c = instance["c"]
        ready = instance["ready_time"]
        due_date = instance["deadline"]
        service = instance["service"]
        model = dp.Model(float_cost = True)
        customer = model.add_object_type(number = n)
        unvisited = model.add_set_var(object_type = customer, target = list(range(1, n)))
        location = model.add_element_var(object_type = customer, target = 0)
        load = None
        vehicle = None
        time = None
        if resource:
            load = model.add_int_resource_var(target = 0, less_is_better = True)
            vehicle = model.add_int_resource_var(target = 1, less_is_better = True)
            time = model.add_float_resource_var(target = 0.0, less_is_better = True)
        else:
            load = model.add_int_var(target = 0)
            vehicle = model.add_int_var(target = 1)
            time = model.add_float_var(target = 0.0)

        weight = model.add_int_table(d)
        travel_cost = model.add_float_table(c)
        initial_time = model.add_int_table(ready)
        deadline = model.add_int_table(due_date)
        service_time = model.add_int_table(service)
        model.add_base_case([unvisited.is_empty(), location == 0])

        for j in range(1, n):
            visit_from_location = dp.Transition(
                name = "visit {}".format(j),
                cost = travel_cost[location, j] + dp.FloatExpr.state_cost(),
                effects = [(unvisited, unvisited.remove(j)),
                        (location, j),
                        (load, load + weight[j]),
                        (time, service_time[j] + dp.max(time + travel_cost[location, j], initial_time[j]))
                        ],
                preconditions = [load + weight[j] <= q, unvisited.contains(j), time + travel_cost[location, j] <= deadline[j]]
            )
            model.add_transition(visit_from_location)

        for j in range(1, n):
            visit_from_depot = dp.Transition(
                name = "visit {} with a new vehicle".format(j),
                cost = travel_cost[location, 0] + travel_cost[0, j] + dp.FloatExpr.state_cost(),
                effects = [
                    (unvisited, unvisited.remove(j)),
                    (location, j),
                    (load, weight[j]),
                    (vehicle, vehicle + 1),
                    (time, service_time[j] + dp.max(travel_cost[location, j], initial_time[j]))
                ],
                preconditions = [vehicle < m, unvisited.contains(j), travel_cost[location, j] <= deadline[j]]
            )
            model.add_transition(visit_from_depot)

        return_to_depot = dp.Transition(
            name = "return",
            cost = travel_cost[location, 0] + dp.FloatExpr.state_cost(),
            effects = [(location, 0)],
            preconditions = [unvisited.is_empty(), location != 0]
        )

        model.add_transition(return_to_depot)

        model.add_state_constr((m - vehicle + 1) * q - load >= weight[unvisited])

        model.add_state_constr(time + travel_cost[location, 0] <= deadline[0])

        if bound:
            min_to = model.add_float_table(
                [min(c[k][j] for k in range(n) if k != j) for j in range(n)]
            )
            model.add_dual_bound(min_to[unvisited] + (location!=0).if_then_else(min_to[0],0))

            min_from = model.add_float_table(
                [min(c[j][k] for k in range(n) if k != j) for j in range(n)]
            )
            model.add_dual_bound(min_from[unvisited] + (location!=0).if_then_else(min_from[location],0))
        return model
    
    def build_path(self, solution):
        paths = []
        path = []
        vehicles = 1
        for t in solution.transitions:
            if "return" not in t.name:
                match = re.search(r"\d+\.?\d*", t.name)  # Matches integers or decimals
                customer = int(match.group()) if match else None  # Convert to float if found
                if "vehicle" in t.name:
                    vehicles +=1
                    paths.append(path)
                    path = []
                path.append(customer)
        if path:
            paths.append(path)
        return vehicles, paths


    def solve(self, instance, best_known, time_limit, resource=True, bound=True):
        model = self.define_model(instance, resource, bound)
        terminated = False
        solver = dp.LNBS(model, time_limit=time_limit, quiet=True)
        solution_costs = []
        times = []
        times.append(0)
        solution_costs.append(None)
        while not terminated:
            solution, terminated = solver.search_next()
            times.append(solution.time)
            solution_costs.append(round(solution.cost,1))
        times.append(time_limit)    
        vehicles, solution_path = self.build_path(solution)
        return vehicles, solution_path, solution_costs[-1], primal_integral(times, solution_costs, best_known), primal_gap(solution_costs[-1], best_known)

    
    
    




