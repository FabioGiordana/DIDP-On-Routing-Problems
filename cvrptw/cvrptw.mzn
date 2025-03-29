include "globals.mzn";
include "gecode.mzn";

%parameters
int: m;  %vehicles
int: n;  %customers
int: q;  %capacity
array [1..n+2*m] of int: d;  %demand
array [1..n+2*m, 1..n+2*m] of int: c;  %travel cost
array [1..n+2*m] of int: ready_time;
array[1..n+2*m] of int: deadline;
array[1..n+2*m] of int: service;
int: lower_b; %lower_bound
int: upper_b; %upper_bound

%variables
array[1..n+2*m] of var 1..n+2*m: pred;  
array[1..n+2*m] of var 1..m: assign;
var int: distance = sum([c[pred[i], i] | i in 1..n+2*m]);
array[1..n+2*m] of var int: time;
var int: vehicles = max([assign[j] | j in 1..n]);


%constraints
%lower_bound
constraint distance >= lower_b;
constraint distance <= upper_b;

%hamiltonian cycle
constraint circuit(pred);

%consistency between start and end nodes
constraint forall(i in n+2..n+m)(
    pred[i] = i+m-1
);

constraint pred[n+1] =n+2*m;

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
constraint forall(i in 1..n)(
    assign[i] = assign[pred[i]]
);

%arrival time for the start nodes is 0
constraint forall(i in n+1..n+m)(
    time[i] = 0
);

%arrival time for customers
constraint forall(i in 1..n)(
    time[i] = max(time[pred[i]] + service[pred[i]] + c[pred[i], i], ready_time[i])
);

%arrival time for end nodes
constraint forall(i in n+m+1..n+2*m)(
    time[i] = max(time[pred[i]] + service[pred[i]] + c[pred[i], i], ready_time[i])
);


%constraint over the deadline for each node
constraint forall(i in 1..n+2*m)(
    time[i] <= deadline[i]
);

solve :: seq_search([
    int_search(pred, dom_w_deg, indomain_random),
    int_search(assign, dom_w_deg, indomain_random),
    relax_and_reconstruct(pred, 85),
    restart_luby(100)
]) minimize vehicles/m + distance/upper_b;

output ["pred = \(pred), obj = \(distance)"];












