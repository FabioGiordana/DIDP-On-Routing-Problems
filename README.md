# Domain-Independent Dynamic Programming on CVRP

## Introduction
Definition of [domain-independent dynamic programming](https://didp.ai/) models to solve variants of capacitated vehicle routing problems.

## Description
The CVRP variants explored are:
* CVRP-TW
* Min-Max CVRP (The objective is to minimize the maximum distance of a single vehicle.)

For CVRP-TW, the effectiveness of redundant information (in the form of resource variables and dual bounds) is tested. As a comparison, the same benchmark instances are solved by CP and [the LKH-3 solver](http://webhotel4.ruc.dk/~keld/research/LKH-3/). The instances used are the Solomon Benchmark Instances](http://web.cba.neu.edu/~msolomon/problems.htm). For DIDP and CP, primal gap and primal integral are computed.

The Min-Max CVRP explored is the one already studied in the repo [Multiple Couriers Problem](https://github.com/FabioGiordana/Multiple-Couriers-Problem) to evaluate the performance of DIDP against well-known and established optimization approaches.

# Author
* [Fabio Giordana](https://github.com/FabioGiordana)
