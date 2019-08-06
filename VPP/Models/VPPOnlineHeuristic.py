#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from gurobipy import *
import parseData
import numpy as np

#timestamps n realizations m
n = 96
m = 50

#price data from GME
cGrid = parseData.parse_data_gme('PricesGME.csv')
cGridSt = np.mean(cGrid)
#capacities and prices
listc = []
objX = np.zeros((m,n))
objTot= range(m)
objList = []
objFinal = []
a1= range(n)
a2= range(n)
a3= range(n)
a4= range(n)
a5= range(n)
a6= range(n)
a7= range(n)
a8= range(n)
a9= range(n)
a10= range(n)
cap = range(n)
change = range(n)
phi = range(n)
notphi = range(n)
capMax = 600
inCap = 200
cDiesel = 0.054
eff = 0.9
cGridS = 0.035
cRU = 0.045

pDieselMax = 800
pDiesel = range(n)
pStorageIn = range(n)
pStorageOut = range(n)
pGridIn = range(n)
pGridOut = range(n)
tilde_cons = range(n)
runtime = 0
phiX = 0
ubStIn = 400
ubStOut = 400
trace_solutions = np.zeros((m,n,9))

totCons = np.load('realizationsLoad.npy')
pRenPV = np.load('realizationsPV.npy')
shift = np.load('realizationsShift.npy')


for j in range(m):
    print 'Realization',j,'resolution:'
    for i in range(n):

    #create a model
        mod = Model()

    #build variables and define bounds
        pDiesel[i] = mod.addVar(vtype=GRB.CONTINUOUS, name="pDiesel_"+str(i))
        pStorageIn[i] = mod.addVar(vtype=GRB.CONTINUOUS, name="pStorageIn_"+str(i))
        pStorageOut[i] = mod.addVar(vtype=GRB.CONTINUOUS, name="pStorageOut_"+str(i))
        pGridIn[i] = mod.addVar(vtype=GRB.CONTINUOUS, name="pGrid_"+str(i))
        pGridOut[i] = mod.addVar(vtype=GRB.CONTINUOUS, name="pGrid_"+str(i))
        cap[i] = mod.addVar(vtype=GRB.CONTINUOUS, name="cap_"+str(i))
        change[i] = mod.addVar(vtype=GRB.INTEGER, name="change")
        phi[i] = mod.addVar(vtype=GRB.BINARY, name="phi")
        notphi[i] = mod.addVar(vtype=GRB.BINARY, name="notphi")

    #################################################
    #Shift from Demand Side Energy Management System
    #################################################


        tilde_cons[i] = (shift[i]+totCons[j][i])
        
    ####################
    #Model constraints
    ####################
    
        mod.addConstr(notphi[i]==1-phi[i])
        mod.addGenConstrIndicator(phi[i], True, pStorageOut[i], GRB.LESS_EQUAL, 0)
        mod.addGenConstrIndicator(notphi[i], True, pStorageIn[i], GRB.LESS_EQUAL, 0)
        
    #power balance constraint
        mod.addConstr((pRenPV[j][i]+pStorageOut[i]+pGridOut[i]+pDiesel[i]-pStorageIn[i]-pGridIn[i] == tilde_cons[i]), "Power balance")

    #Storage cap
        if i==0:
            mod.addConstr(cap[i]==inCap)
        
            mod.addConstr(cap[i]<=capMax)
            mod.addConstr(cap[i]>=0)

            mod.addConstr(pStorageIn[i]<=capMax-(inCap))
            mod.addConstr(pStorageOut[i]<=inCap)
        else:
            mod.addConstr(cap[i]==capX+eff*pStorageIn[i]-eff*pStorageOut[i])
            
            mod.addConstr(cap[i]<=capMax)
            mod.addConstr(cap[i]>=0)
            
            mod.addConstr(pStorageIn[i]<=capMax-(capX))
            mod.addConstr(pStorageOut[i]<=capX)
        
        mod.addConstr(pStorageIn[i]<=ubStIn)
        mod.addConstr(pStorageOut[i]<=ubStOut)
        


    #Diesel and Net cap

        mod.addConstr(pDiesel[i]<=pDieselMax)

    #Storage mode change

        mod.addConstr(change[i]>=0)

        mod.addConstr(change[i]>= (phi[i] - phiX))
        mod.addConstr(change[i]>= (phiX - phi[i]))


    #build objective (only Power with direct costs)

        mod.setObjective(cGrid[i]*pGridOut[i]+cDiesel*pDiesel[i]+cGridSt*pStorageIn[i]-cGridS*pGridIn[i]+change[i]*cRU)

    # Optimize VPP planning Model
        def solve():
            mod.optimize()
            status = mod.status
            if status == GRB.Status.INF_OR_UNBD or status == GRB.Status.INFEASIBLE \
                or status == GRB.Status.UNBOUNDED:
                print('The model cannot be solved because it is infeasible or \
                      unbounded')
                exit(1)
            
            if status != GRB.Status.OPTIMAL:
                print('Optimization was stopped with status %d' % status)
                exit(0)
        solve()
        runtime += mod.Runtime
        

        #extract x values
        a2[i] = pDiesel[i].X
        a4[i]  = pStorageIn[i].X
        a5[i]  = pStorageOut[i].X
        a3[i] = pRenPV[j][i]
        a6[i] = pGridIn[i].X
        a7[i] = pGridOut[i].X
        a8[i] = cap[i].X
        a1[i] = tilde_cons[i]
        objX[j][i] = mod.objVal
        a9[i] = cGrid[i]
        capX = cap[i].x
        listc.append(capX)
        phiX = phi[i].x

        trace_solutions[j][i] = [mod.objVal, a3[i], a1[i], capX, a2[i], a4[i], a5[i], a6[i], a7[i]]
        objList.append(objX[j][i])

    a10 = shift
    data = np.array([a1, a2, a3, a9, a6, a7, a4, a5, a8, a10])
    for k in range(0, len(objList), 96):
        ob = sum(objList[k:k+96])
    objFinal.append(ob)
    med = np.mean(objFinal)
    var = np.std(objFinal)
    print "============================== Solutions ================================="
    print "Solution cost for each realization: "
    print objFinal
    print "The mu cost over %d realizations is %f and standard deviation is %f" %(m,med,var)
    print "The runtime is %f sec" %((runtime*60)/m)

