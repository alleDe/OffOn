#!/usr/bin/env python

import csv
import sys
import warnings
import numpy as np


#parse Load
def parse_data_load(fname):
    # prepare a list for the results
    load = []
    load_hour = []
    
    # open the input file
    f = open( fname, 'rU' )
    for line in f:
        cells = line.split( "," )
        coln = len(cells)-1
        load.append( float( cells[coln] ) )

    n=3
    load_hour = [sum(load[x:x+n]) for x in range (0,len(load),n)]

    return load_hour


#parse GME market prices
def parse_data_gme(fname):
    # prepare a list for the results
    prices_gme = []

    # open the input file
    with open(fname, 'rU') as fin:
        reader = csv.reader(fin)
        for i, row in enumerate(reader):
            if i > 0:
                # each data point is a pair:
                # - the first item is an hour
                # - the second item is the grid electricity price
                if (int(row[0]) > 23):
                    print('ERROR: invalid hour in: ' + str(row))
                else:
                
                    prices_gme.append(float(row[1])/1000)
    price_gme_96 = []
    gme=np.asarray(prices_gme)
    
    for i in range(24):
        price_gme_96.append(gme[i])
        price_gme_96.append(gme[i])
        price_gme_96.append(gme[i])
        price_gme_96.append(gme[i])

    # return the read data
    return price_gme_96

#parse PV production
def parse_data_PV(fname):
    # prepare a list for the results
    PV = []
    PVhour = []
    f = open( fname, 'rU' )
    for line in f:
        cells = line.split( "," )
        coln = len(cells)-1
        PV.append( float( cells[coln] ) )

    n=3
    PVhour = [sum(PV[x:x+n]) for x in range (0,len(PV),n)]

    return PVhour

#ideal load
def ideal_cons():
    np.random.seed(3)
    n=96
    real_cons = parse_data_load('Load_Profiles.csv')
    real_cons1 = parse_data_load('Load_Profiles1.csv')
    
    #data aggr
    tot_cons = [real_cons[i]+real_cons1[i] for i in range(n)]

    ideal_cons = range(n)
    for i in range(n):
        if (i<24):
            ideal_cons[i] = tot_cons[i]*(1 + 0.01 * np.random.sample())
        elif (i>=24 and i <76):
            ideal_cons[i] = tot_cons[i]*(1 - 0.01 * np.random.sample())
        else:
            ideal_cons[i] = tot_cons[i]*(1 + 0.01 * np.random.sample())

    return ideal_cons

