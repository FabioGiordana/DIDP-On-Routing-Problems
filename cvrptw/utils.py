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

        
    