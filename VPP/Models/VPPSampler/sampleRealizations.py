#!/usr/bin/env python

from scipy.stats import norm
import matplotlib.pyplot as plt
import numpy as np
import parseData
import random

n=96
m = 100
t_base = 3
np.random.seed(3)

samplePV = np.zeros((m,n))
sampleLoad = np.zeros((m,n))
tot_cons = range(n)
tot_cons2 = range(n)
tot_cons3 = range(n)

#PV generation
pRenPV = parseData.parse_data_PV('PV_Profiles.csv')

#load data
real_cons = parseData.parse_data_load('Load_Profiles.csv')
real_cons1 = parseData.parse_data_load('Load_Profiles1.csv')

#data norm
for i in range(n):
    tot_cons[i] = real_cons[i]+real_cons1[i]

#based on parsed data, this function create t_base modified input of PV profiles
def PV_f():
    for j in range(t_base):
        for i in range(n):
            if(pRenPV[i]==0):
                samplePV[j][i]=0
            if (i<12):
                samplePV[j][i] = pRenPV[i]*(1 + 0.1 * np.random.sample())
            else:
                samplePV[j][i] = pRenPV[i]*(1 - 0.1 * np.random.sample())

    return samplePV

#print "**************SAMPLE PV PRODUCTION*******************"
#print PV_f()

#based on parsed data, this function creates t_base modified input of load profiles
def Load_f():
    for j in range(t_base):
        for i in range(n):
            if (i<12):
                sampleLoad[j][i] = tot_cons[i]*(1 + 0.1 * np.random.sample())
            elif (i>=12 and i <19):
                sampleLoad[j][i] = tot_cons[i]*(1 + 0.2 * np.random.sample())
            else:
                sampleLoad[j][i] = tot_cons[i]*(1 + 0.3 * np.random.sample())
    return sampleLoad

#print "**************SAMPLE LOAD*****************************"
#print Load_f()

np.save('../realizationsLoad.npy', Load_f())
np.save('../realizationsPV.npy', PV_f())

#create m realizations based on weighted choice of t_base realizations
load = np.load('../realizationsLoad.npy')

elements = load.tolist()

weights = [0.3, 0.3, 0.3]

choicesL = sum([[element] * int(weight * 100)for element, weight in zip(elements, weights)], [])
for i in range(m):
    elements[i] = random.choice(choicesL)
np.save('../realizationsLoad.npy', np.asarray(elements))
loadRand = np.load('../realizationsLoad.npy')

pv = np.load('../realizationsPV.npy')
elements = pv.tolist()
weights = [0.3, 0.3, 0.3]
# get "sum" of result list of lists 
choicesP = sum([[element] * int(weight * 100)for element, weight in zip(elements, weights)], [])
for i in range(m):
    elements[i] = random.choice(choicesP)
np.save('../realizationsPV.npy', np.asarray(elements))
pvRand = np.load('../realizationsPV.npy')

