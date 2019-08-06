# OffOn

How to Tame Your Anticipatory Algorithm

Given an arbitrary anticipatory algorithm, we present methods that allow to retain its solution quality at a fraction of the online computational cost, via a substantial degree of offline preparation.

We ground our techniques on two case studies: an energy management system with uncertain renewable generation and load demand (Virtual Power Plant (VPP)), and a Traveling Salesman Problem with uncertain travel times (TSP).

The input anticipatory algorithms for both our cases studies are based on the models from [De Filippo et al., 2018]. This simply consists in applying the Sample Average Approximation (SAA) to a relaxed version of the multistage problem, where non-anticipativity constraints between future stages are ignored. We used it to define the input algorithm A for both our case studies.

The models of uncertainty for both cases studies are technically mixtures of Gaussians. They are designed to ensure a realistic level of dependence between the random variables.
For the VPP, we assume that both the RES power generation and the load at each stage may exhibit Normally distributed deviations from a number of different possible behaviors.
The model for the TSP is based on similar ideas, but makes use of a more complex sampling process. We assume that the travel times of all arcs from a given node follow a Normal distribution, whose mean and variance is controlled by an additional (binary) random variable.

As an underlying solver we use Gurobi, which can handle both MILPs and Quadratic Programs.




