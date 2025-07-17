include "globals.mzn";
include "gecode.mzn";

%parameters
int: m;  %vehicles
int: n;  %customers
int: q;  %capacity
array [1..n+2*m] of int: d;  %demand
array [1..n+2*m, 1..n+2*m] of int: c;  %travel cost;
int: lower_b; %lower_bound
int: upper_b; %upper_bound


%variables
array[1..n+2*m] of var 1..n+2*m: path;  
array[1..n+2*m] of var 1..m: assign;
array[1..m] of var int: distance= [sum([c[i, path[i]] | i in 1..n+2*m where assign[i]==j]) | j in 1..m];


%constraints
%lower_bound
constraint max(distance) >= lower_b;
constraint max(distance) <= upper_b;

%hamiltonian cycle
constraint circuit(path);

%consistency between start and end nodes
constraint forall(i in n+m+1..n+2*m-1)(
    path[i] = i-m+1
);

constraint path[n+2*m] = n+1;

%packing constraint for loads
constraint bin_packing(q, assign, d);

%vehicle assignment for start nodes
constraint forall(i in 1..m)(
    assign[n+i] = i
);

%vehicle assignment for end nodes
constraint forall(i in 1..m)(
    assign[n+m+i] = i
);

%chanelling between variables
constraint forall(i in 1..n+m)(
    assign[i] == assign[path[i]]
);


solve :: seq_search([
    int_search(path, dom_w_deg, indomain_random),
    int_search(assign, dom_w_deg, indomain_random),
    relax_and_reconstruct(path, 85),
    restart_luby(100)
]) minimize max(distance);

output ["path = \(path), obj = \(max(distance)), assign = \(assign)"];