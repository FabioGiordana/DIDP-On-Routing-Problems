import math

def primal_gap(solution_cost, best_known):
    if solution_cost is None or solution_cost*best_known < 0:
        return 1
    elif solution_cost==best_known==0:
        return 0
    else:
        return abs(solution_cost - best_known)/(max(abs(solution_cost), abs(best_known)))
    
def primal_integral(times, solution_costs, best_known):
    integral = 0
    for i in range(1, len(times)):
        gap = primal_gap(solution_costs[i-1], best_known)
        integral += gap*(times[i]-times[i-1])
    return integral

def check_solution(solution_paths, solution_cost, instance):
    n = instance["n"]
    m = instance["m"]
    q = instance["q"]
    d = instance["d"]
    c = instance["c"]
    visited_nodes = []
    max_distance = 0
    vehicles = 0
    for path in solution_paths:
        vehicles += 1
        load = 0
        distance = 0
        prev = 0
        for location in path:
            if location in visited_nodes:
                print(f"====================Location visited twice====================")
            visited_nodes.append(location)
            load += d[location]
            if load > q:
                print(f"====================Load exceed====================")
            distance += c[prev][location]
            prev = location
        distance += c[prev][0]
        max_distance = max(distance, max_distance)
    if not math.isclose(max_distance, solution_cost):
        print(f"====================Distance {max_distance} different from solution cost {solution_cost}====================")
    if vehicles > m:
        print("====================Vehicles exceed====================")
    if len(visited_nodes) + 1 != n:
        print(f"====================Number of visited customers {len(visited_nodes)} different from {n}====================")
