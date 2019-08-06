
###################### TSP Online Heuristic ####################
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gurobipy import *
import numpy as np
import time

time_start = time.clock()
n = 20 #number of clients
positions = range(n)
vehicles = range(1) #one single vehicle
clients = positions[1:]
print clients
samples = range(50) # number of realizations
total_cost = 0
l_print = []
tim=0

print "Number of clients: " + str(len(clients))

s=0
sum1=0

cost_samples = np.load('tspsamples.npy')

x1={}
list_nodes=[[] for k in vehicles]
list_nodes1=[[] for k in vehicles]
count_v = range(len(vehicles))

for k in vehicles:
    for i in clients:
        list_nodes[k].append(i)
        list_nodes1[k].append(i)
list_temp = [[] for k in vehicles]

list_cost = range(len(samples))

#online routing decisions
print '\nOnline Routing Decisions:'
for sa in samples:
    s=0
    sum=0
    
    list_optimal_sol = [[] for k in vehicles]
    h=0
    total_cost = 0
    for k in vehicles:
        
        for i in clients:
            list_temp[k].append(i)
        
        for h in range(len(list_temp[k])):
            
            #model
            model = Model('TSPMyopicHeuristic')
            
            for j in list_temp[k]:
                x1[j] = model.addVar(vtype=GRB.BINARY,name="route_h")
            
            model.addConstr(quicksum(x1[j] for j in list_temp[k]) == 1)
            
            o1 = quicksum(cost_samples[sa][h][j]*x1[j] for j in list_temp[k] if j!=h)
            model.setObjective(o1,GRB.MINIMIZE)
            model.setParam('OutputFlag',False)
            model.optimize()

            total_cost += model.objVal
            tim += model.Runtime
    
            for j in list_temp[k]:
                if x1[j].x>0:
                    h=j
                    list_temp[k].remove(j)
                    list_optimal_sol[k].append(j)

    print '\nRealization %d: ' %(sa)
    for k in vehicles:
        list_optimal_sol[k].insert(0,0)
        list_optimal_sol[k].append(0)
        print list_optimal_sol[k]
    print total_cost
    l_print.append(total_cost)

print "\n"
print "================== solutions ======================"
#print cost for each realization
print l_print

med = np.mean(l_print)
var = np.sqrt(np.std(l_print))
print "\n"

#print cost, standard dev, runtime
print "average travel time over %d realizations:" %(s)
print med
print "standard deviation over %d realizations:" %(s)
print var
print "runtime:"
print tim

