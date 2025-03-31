import didppy as dp
import re
from collections import defaultdict

class DIDPModel():

    def define_model(self, instance):
        m = instance[0]
        n = instance[1]
        q = instance[2]
        w = instance[3]
        c = instance[4]
        model = dp.Model()

        customer = model.add_object_type(number = n)

        unvisited = model.add_set_var(object_type = customer, target = list(range(n)))

        locations = []
        for _ in range(m):
            location = model.add_element_var(object_type = customer, target = n)
            locations.append(location)

        partial_costs = []
        for _ in range(m):
            p = model.add_int_resource_var(target = 0, less_is_better=True)
            partial_costs.append(p)

        partial_loads = []
        for _ in range(m):
            p = model.add_int_resource_var(target = 0, less_is_better=True)
            partial_loads.append(p)

        vehicles = model.add_int_resource_var(target=0, less_is_better=False)

        capacities = model.add_int_table(q)

        weight = model.add_int_table(w)

        travel_cost = model.add_int_table(c)

        model.add_base_case([unvisited.is_empty()] + [l==n for l in locations])

        for k in range(m):
            for j in range(n):
                start_path = dp.Transition(
                    name = f"visit {j+1} from the depot with vehicle {k+1}",
                    cost = dp.max(dp.IntExpr.state_cost(), travel_cost[n, j]),
                    effects = [(unvisited, unvisited.remove(j)),
                            (locations[k], j),
                            (partial_costs[k], travel_cost[n, j]),
                            (partial_loads[k], weight[j]),
                            (vehicles, vehicles+1)],
                    preconditions = [unvisited.contains(j), partial_loads[k] + weight[j] <= capacities[k], locations[k]==n]
                )
                model.add_transition(start_path)

        for k in range(m):
            for j in range(n):
                visit_from_location = dp.Transition(
                    name = f"visit {j+1} with vehicle {k+1}",
                    cost = dp.max(dp.IntExpr.state_cost(), travel_cost[locations[k], j] + partial_costs[k]),
                    effects = [(unvisited, unvisited.remove(j)),
                            (locations[k], j),
                            (partial_costs[k], partial_costs[k] + travel_cost[locations[k], j]),
                            (partial_loads[k], partial_loads[k] + weight[j])],
                    preconditions = [unvisited.contains(j), partial_loads[k] + weight[j] <= capacities[k], locations[k]!=n]
                )
                model.add_transition(visit_from_location)

        for k in range(m):
            visit_depot = dp.Transition(
            name = f"return to depot with vehicle {k+1}",
            cost = dp.max(travel_cost[locations[k], n] + partial_costs[k], dp.IntExpr.state_cost()),
            effects = [(locations[k], n)],
            preconditions = [unvisited.is_empty(), locations[k] != n]
        )
            model.add_transition(visit_depot)

        lower_bound = max([c[n][i] + c[i][n] for i in range(n-1)])
        model.add_dual_bound(lower_bound)
        return model
    
    def build_path(self, solution):
        vehicle_paths = defaultdict(list)
        for t in solution.transitions:
            match = re.search(r'visit (\d+) .*vehicle (\d+)', t.name)
            if match:
                location, vehicle = match.groups()
                vehicle_paths[int(vehicle)].append(int(location))
        return [vehicle_paths[key] for key in sorted(vehicle_paths.keys())]


    def solve(self, instance, time_limit):
        model = self.define_model(instance)
        solver = dp.LNBS(model, time_limit=time_limit, quiet=True, f_operator=dp.FOperator.Max)
        solution = solver.search()
        solution_path = self.build_path(solution)
        solution_cost = solution.cost
        return solution_cost, solution_path, solution.is_optimal, solution.time

    


    
