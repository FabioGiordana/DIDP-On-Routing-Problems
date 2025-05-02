include "globals.mzn";
include "gecode.mzn";

%parameters
int: n;  %customers (1 is the depot)
int: m;  %vehicles
int: q;  %capacity
array [1..n] of int: d;  %demand
array [1..n, 1..n] of int: c;  %travel cost
int: lower_b; %lower_bound
int: upper_b; %upper_bound

%variables
array[1..m, 1..n] of var 1..n: pred; 
array[2..n] of var 1..m: assign;
array[1..m] of var int: distance = [sum([c[pred[i,j],j] | j in 1..n where pred[i,j]!=j]) | i in 1..m];


%constraints
%lower_bound
constraint max(distance) >= lower_b;
constraint max(distance) <= upper_b;

%sub-hamiltonian cycles
constraint forall(i in 1..m)(subcircuit(pred[i,..]));

%each item assigned once
constraint forall(j in 2..n)(count(pred[..,j], j, m-1));   

%use all vehicles
constraint forall(i in 1..m)(pred[i, 1] != 1);

%capacity constraint
constraint bin_packing(q, assign, array1d(2..n, [d[j] | j in 2..n]));

%chanelling between variables
constraint forall(i in 1..m, j in 2..n)(
    assign[j] == i <-> pred[i,j] != j
);


solve :: seq_search([
    int_search(pred, dom_w_deg, indomain_random),
    int_search(assign, dom_w_deg, indomain_random),
    relax_and_reconstruct(array1d(pred), 85),
    restart_luby(100)
]) minimize max(distance);

output ["pred = \(pred), obj = \(max(distance))"];












