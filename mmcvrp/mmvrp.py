import didppy as dp

def read_instances_min_max(n):
    #open the specified instance file and compute the parameters
    instance = []
    file = open(f"Instances/inst{n:02}.dat")
    
    l = 0
    distances = []
    for line in file.readlines():
        line = line.strip()
        if l < 2:
            instance.append(int(line))
        elif l < 4:
            tmp = []
            for part in line.split():
                tmp.append(int(part))
            instance.append(tmp)
        else:
            tmp = []
            for part in line.split(" "):
                tmp.append(int(part))
            distances.append(tmp)
        l += 1
    instance.append(distances)
    return instance

def solve(n, m, q, w, c):
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

    min_to = model.add_float_table(
        [min(c[k][j] for k in range(n) if k != j) for j in range(n)]
    )


    solver = dp.LNBS(model, time_limit=60)
    solution = solver.search()

    print("Transitions to apply:")
    print("")

    for t in solution.transitions:
        print(t.name)

    print("")
    print("Cost: {}".format(solution.cost))
    return solution
    


    
