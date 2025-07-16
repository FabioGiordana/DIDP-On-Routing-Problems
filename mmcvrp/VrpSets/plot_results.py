import json
import matplotlib.pyplot as plt
import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from utils import primal_gap, primal_integral
from collections import Counter

methods = {"DIDP_Complete": "DIDP_Complete",
           "DIDP_No_Bound": "DIDP_Implied",
           "DIDP_No_Implied": "DIDP_Bound",
           "DIDP_Base": "DIDP_Base",
           #"CP_Model": "CP_Model",
           "DIDP_No_Implied_Opt": "DIDP_Bound_Opt",
           "DIDP_Base_Opt": "DIDP_Base_Opt"}
           #"CP_Model_No_Imp": "Cp_Model_No_Imp"}

results = ["A", "M", "Golden"]
                

def init_dict():
    d = {}
    for m in methods.keys():
        d[m] = {0.0 : 0.0}
    return d


def save_solutions(d, title, x_title, filename):
    dir = "Plots"
    os.makedirs(dir, exist_ok=True)
    plt.figure(figsize=(8, 5))
    for m in methods.keys():
        x_vals = list(d[m].values())
        y_vals = list(d[m].keys())
        plt.plot(x_vals, y_vals, marker='o', label=methods[m])
    
    plt.xlabel(x_title)
    plt.ylabel("Ratio of Instances")
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.savefig(f"{dir}/{filename}")
    plt.close()
    

    
def best_solution(filename):
    with open(f"{filename}.json", "r") as file:
        data = json.load(file)
        best_known = sys.maxsize
        for m in methods.keys():
            cost = data[m]["Best Cost: "]
            if cost is not None and cost < best_known:
                best_known = cost
    if best_known == sys.maxsize:
        print(f"No solution found for {filename}")
    return best_known

def retrieve_info(filename, method):
    with open(f"{filename}.json", "r") as file:
        data = json.load(file)
        paths = data[method]["Best Path: "]
        vehicles = len(paths) if paths is not None else None
        return data[method]["Solution Costs: "], data[method]["Times: "], vehicles

def save_table(filename, data):
    dir = "Plots"
    os.makedirs(dir, exist_ok=True)

    doc = SimpleDocTemplate(f"{dir}/{filename}", pagesize=A4)

    # Calculate usable width
    page_width = A4[0]
    left_margin = right_margin = 72
    usable_width = page_width - left_margin - right_margin
    num_cols = len(data[0])
    col_width = usable_width / num_cols
    col_widths = [col_width] * num_cols

    # Create table
    table = Table(data, colWidths=col_widths)

    # Base style
    style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ])

    # Apply red text for values different from row mode
    for row_idx, row in enumerate(data[1:], start=1):  # Skip header (row 0)
        # Find the most frequent value in the row
        freq = Counter(row)
        mode_val, _ = freq.most_common(1)[0]

        for col_idx, cell in enumerate(row):
            if cell != mode_val:
                style.add('TEXTCOLOR', (col_idx, row_idx), (col_idx, row_idx), colors.red)

    table.setStyle(style)
    doc.build([table])


def plot_solutions():
    os.makedirs("Plots", exist_ok=True)
    all_integral = init_dict()
    all_gap = init_dict()
    all_count = 1
    all_total = 0
    for g in results:
        folder = f"Results/{g}"
        instances = Path(folder).rglob("*.json")
        instances = list(instances)
        all_total += len(instances)
    for g in results:
        cumulative_integral = init_dict()
        cumulative_gap = init_dict()
        folder = f"Results/{g}"
        instances = Path(folder).rglob("*.json")
        instances = list(instances)
        total = len(instances)
        count = 1
        header = ["Instance"] + list(methods.values())
        table = [header]
        for filepath in instances:
            filepath = str(filepath.stem)
            best_known = best_solution(f"Results/{g}/{filepath}")
            row = [filepath]
            for m in methods.keys():
                solutions, times, vehicles = retrieve_info(f"Results/{g}/{filepath}", m)
                row.append(vehicles)
                if solutions is None:
                    solutions = [None]
                integral = primal_integral(times, solutions, best_known)
                gap = primal_gap(solutions[-1], best_known)
                cumulative_integral[m][count/total] = cumulative_integral[m][(count-1)/total] + integral
                all_integral[m][all_count/all_total] = all_integral[m][(all_count-1)/all_total] + integral
                cumulative_gap[m][count/total] = cumulative_gap[m][(count-1)/total] + gap 
                all_gap[m][all_count/all_total] = all_gap[m][(all_count-1)/all_total] + gap
            table.append(row)
            count += 1
            all_count += 1

        save_table(f"Vehicles_{g}.pdf", table)
        save_solutions(cumulative_integral, f"Primal Integral for {g} benchmark instances", 
                       "Primal integral", f"Integral_{g}.jpg")
        save_solutions(cumulative_gap, f"Primal Gap for {g} benchmark instances", 
                       "Primal gap", f"Gap_{g}.jpg")
    save_solutions(all_integral, f"Primal Integral for all the benchmark instances", 
                       "Primal integral", f"Integral_Total.jpg")
    save_solutions(all_gap, f"Primal Gap for all the benchmark instances", 
                       "Primal gap", f"Gap_Total.jpg")
    



        
if __name__ == "__main__":
    plot_solutions()