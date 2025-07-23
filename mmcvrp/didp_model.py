import didppy as dp
import re
from collections import defaultdict
from utils import check_solution


class DIDPModel():

    def define_opt_model(self, instance, bound=True):
        n = instance["n"]
        m = instance["m"]
        q = instance["q"]
        d = instance["d"]
        c = instance["c"]
        model = dp.Model(float_cost = True)
        customer = model.add_object_type(number = n)
        unvisited = model.add_set_var(object_type = customer, target = list(range(1, n)))
        
        locations = []
        for _ in range(m):
            location = model.add_element_var(object_type = customer, target = 0)
            locations.append(location)

        partial_costs = []
        for _ in range(m):
            p = model.add_float_resource_var(target = 0.0, less_is_better=True)
            partial_costs.append(p)

        partial_loads = []
        for _ in range(m):
            p = model.add_int_resource_var(target = 0, less_is_better=True)
            partial_loads.append(p)
            
        weight = model.add_int_table(d)
        travel_cost = model.add_float_table(c)

        model.add_base_case([unvisited.is_empty()] + [l==0 for l in locations])

        for k in range(m):
            for j in range(1, n):
                visit_from_location = dp.Transition(
                    name = f"visit {j} with vehicle {k+1}",
                    cost = dp.max(dp.FloatExpr.state_cost(), travel_cost[locations[k], j] + partial_costs[k]),
                    effects = [(unvisited, unvisited.remove(j)),
                            (locations[k], j),
                            (partial_costs[k], partial_costs[k] + travel_cost[locations[k], j]),
                            (partial_loads[k], partial_loads[k] + weight[j])],
                    preconditions = [unvisited.contains(j), partial_loads[k] + weight[j] <= q]
                )
                model.add_transition(visit_from_location)

        for k in range(m):
            visit_depot = dp.Transition(
            name = f"return to depot with vehicle {k+1}",
            cost = dp.max(travel_cost[locations[k], 0] + partial_costs[k], dp.FloatExpr.state_cost()),
            effects = [(locations[k], 0),
                       (partial_costs[k], travel_cost[locations[k], 0] + partial_costs[k])],
            preconditions = [unvisited.is_empty(), locations[k] != 0]
        )
            model.add_transition(visit_depot)

        if bound:
            lower_bound = model.add_float_table([c[0][j] + c[j][0]
                                                for j in range(n)])
            model.add_dual_bound((unvisited.is_empty()).if_then_else(0, lower_bound.max(unvisited)))

        return model

    def define_model(self, instance, bound=True, implied=True):
        n = instance["n"]
        m = instance["m"]
        q = instance["q"]
        d = instance["d"]
        c = instance["c"]
        model = dp.Model(float_cost = True)
        customer = model.add_object_type(number = n)
        unvisited = model.add_set_var(object_type = customer, target = list(range(1, n)))
        
        locations = []
        for _ in range(m):
            location = model.add_element_var(object_type = customer, target = 0)
            locations.append(location)

        partial_costs = []
        for _ in range(m):
            p = model.add_float_resource_var(target = 0.0, less_is_better=True)
            partial_costs.append(p)

        partial_loads = []
        for _ in range(m):
            p = model.add_int_resource_var(target = 0, less_is_better=True)
            partial_loads.append(p)

        vehicles = model.add_int_var(target = 0)
            
        weight = model.add_int_table(d)
        travel_cost = model.add_float_table(c)

        if implied:
            model.add_base_case([unvisited.is_empty()] + [l==0 for l in locations] + [vehicles == m])
        else:
            model.add_base_case([unvisited.is_empty()] + [l==0 for l in locations])

        for k in range(m):
            for j in range(1, n):
                visit_from_location = dp.Transition(
                    name = f"visit {j} with vehicle {k+1}",
                    cost = dp.max(dp.FloatExpr.state_cost(), travel_cost[locations[k], j] + partial_costs[k]),
                    effects = [(unvisited, unvisited.remove(j)),
                            (locations[k], j),
                            (partial_costs[k], partial_costs[k] + travel_cost[locations[k], j]),
                            (partial_loads[k], partial_loads[k] + weight[j])],
                    preconditions = [unvisited.contains(j), partial_loads[k] + weight[j] <= q,
                                     locations[k] != 0]
                )
                model.add_transition(visit_from_location)

        for k in range(m):
            for j in range(1, n):
                visit_from_depot = dp.Transition(
                    name = f"visit {j} from the depot with vehicle {k+1}",
                    cost = dp.max(dp.FloatExpr.state_cost(), travel_cost[0, j]),
                    effects = [(unvisited, unvisited.remove(j)),
                            (locations[k], j),
                            (partial_costs[k], travel_cost[0, j]),
                            (partial_loads[k], weight[j]),
                            (vehicles, vehicles+1)],
                    preconditions = [unvisited.contains(j), locations[k] == 0]
                )
                model.add_transition(visit_from_depot)

        for k in range(m):
            visit_depot = dp.Transition(
            name = f"return to depot with vehicle {k+1}",
            cost = dp.max(travel_cost[locations[k], 0] + partial_costs[k], dp.FloatExpr.state_cost()),
            effects = [(locations[k], 0),
                       (partial_costs[k], travel_cost[locations[k], 0] + partial_costs[k])],
            preconditions = [unvisited.is_empty(), locations[k] != 0]
        )
            model.add_transition(visit_depot)

        if implied:
            model.add_state_constr(unvisited.len() >= m-vehicles)

        if bound:
            lower_bound = model.add_float_table([c[0][j] + c[j][0]
                                                for j in range(n)])
            model.add_dual_bound((unvisited.is_empty()).if_then_else(0, lower_bound.max(unvisited)))

        return model
    
    def define_gtr_model(self, instance, bound, implied):
        n = instance["n"]
        m = instance["m"]
        q = instance["q"]
        d = instance["d"]
        c = instance["c"]
        model = dp.Model(float_cost = True)
        customer = model.add_object_type(number = n)
        unvisited = model.add_set_var(object_type = customer, target = list(range(1, n)))
        
        location = model.add_element_var(object_type = customer, target = 0)
        
        partial_cost = model.add_float_resource_var(target = 0.0, less_is_better=True)

        partial_load = model.add_int_resource_var(target = 0, less_is_better=True)

        vehicles = model.add_int_var(target = 1)
            
        weight = model.add_int_table(d)
        travel_cost = model.add_float_table(c)

        if implied:
            model.add_base_case([unvisited.is_empty(), location==0, vehicles == m])
        else:
            model.add_base_case([unvisited.is_empty(), location==0])

        for j in range(1, n):
            visit_from_location = dp.Transition(
                name = f"visit {j}",
                cost = dp.max(dp.FloatExpr.state_cost(), travel_cost[location, j] + partial_cost),
                effects = [(unvisited, unvisited.remove(j)),
                        (location, j),
                        (partial_cost, partial_cost + travel_cost[location, j]),
                        (partial_load, partial_load + weight[j]),],
                    preconditions = [unvisited.contains(j), partial_load + weight[j] <= q]
                )
            model.add_transition(visit_from_location)

        for j in range(1, n):
            visit_from_depot = dp.Transition(
                name = f"visit {j} with a new vehicle",
                cost = dp.max(dp.FloatExpr.state_cost(), dp.max(travel_cost[0, j], partial_cost + travel_cost[location,0])),
                effects = [(unvisited, unvisited.remove(j)),
                            (location, j),
                            (partial_cost, travel_cost[0, j]),
                            (partial_load, weight[j]),
                            (vehicles, vehicles+1)],
                    preconditions = [unvisited.contains(j), vehicles<m]
                )
            model.add_transition(visit_from_depot)

        visit_depot = dp.Transition(
        name = f"return to depot",
        cost = dp.max(travel_cost[location, 0] + partial_cost, dp.FloatExpr.state_cost()),
        effects = [(location, 0)],
        preconditions = [unvisited.is_empty(), location != 0]
        )
        model.add_transition(visit_depot)

        if implied:
            model.add_state_constr(unvisited.len() >= m-vehicles)

        model.add_state_constr((m - vehicles + 1) * q - partial_load >= weight[unvisited])

        if bound:
            lower_bound = model.add_float_table([c[0][j] + c[j][0]
                                                for j in range(n)])
            model.add_dual_bound((unvisited.is_empty()).if_then_else(0, lower_bound.max(unvisited)))

        return model

    
    def build_path(self, solution):
        vehicle_paths = defaultdict(list)
        for t in solution.transitions:
            print(t.name)
            match = re.search(r'visit (\d+) .*vehicle (\d+)', t.name)
            if match:
                location, vehicle = match.groups()
                vehicle_paths[int(vehicle)].append(int(location))
        return [vehicle_paths[key] for key in sorted(vehicle_paths.keys())]
    
    def build_path_gtr(self, solution):
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
        return paths


    def solve(self, instance, time_limit, bound=True, implied=True, opt=True, gtr=True):
        if opt and implied:
            raise Exception("Optimized model used only without implied constraint")
        if opt:
            model = self.define_opt_model(instance,bound)
        elif gtr:
            model = self.define_gtr_model(instance, bound, implied)
        else:
            model = self.define_model(instance, bound, implied, opt)
        solver = dp.LNBS(model, time_limit=time_limit, quiet=True, f_operator=dp.FOperator.Max)
        terminated = False
        solution_costs = []
        times = []
        times.append(0)
        solution_costs.append(None)
        while not terminated:
            solution, terminated = solver.search_next()
            if solution.cost is None:
                times.append(time_limit)
                return None, times, None, None, False
            if gtr:
                solution_path = self.build_path_gtr(solution)
            else:
                solution_path = self.build_path(solution)
            check_solution(solution_path, solution.cost, instance)
            times.append(solution.time)
            solution_costs.append(round(solution.cost,1))
        times.append(max(times[-1], time_limit))
        return solution_costs, times, solution_costs[-1], solution_path, solution.is_optimal

       