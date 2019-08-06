#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from scipy import stats
from matplotlib import pyplot as plt
np.random.seed(4)

def readdata(fname):
    # Read data
    with open(fname) as fp:
        nnd = 0
        res = None
        for k, lne in enumerate(fp):
            if k == 0:
                nnd = int(lne)
                res = np.zeros((nnd, nnd))
            elif 0 < k <= nnd:
                res[k-1, :] = [float(v) for v in lne.split()]
            else:
                break
    # Apply a correction
    if res is not None:
        for i in range(0, nnd):
            res[i, i] = 0
    return res, nnd


def bsample(p):
    return [stats.bernoulli.rvs(pi) for pi in p]


def nextprob(x, dmat, pauto=0.5, prandom=0.1):
    # Build a probability vector
    nnd = len(x)
    # Compute raw distance-based weights
    rwgt = np.exp(-dmat)
    np.fill_diagonal(rwgt, 0)
    # Compute normalization factor (row vector)
    nwgt = np.sum(rwgt, axis=0)
    # Compute probability weights
    wgt = (1-pauto) * rwgt / nwgt
    np.fill_diagonal(wgt, pauto)
    # Compute new probability
    prb = prandom + (1-2*prandom) * np.matmul(wgt.T, x)
    return prb


def nsample(state, dmat, sigma=0.1):
    res = np.zeros_like(dmat)
    for i, stt in enumerate(state):
        row = dmat[i, :]
        nrvs = stats.norm.rvs(size=len(row))
        res[i, :] = (1+stt)*row + row * sigma * nrvs
    return res


def tspsample(dmat, nsamples,
        prandom=0.2, # capped probability that node is in "short" mode
        pauto=0.6, # raw probability of keeping the state
        sigma=0.1, # relative standard deviation for the Normal distributions
        bootstrap=100, # number of simulated iterations to discard
        step_to_sample_ratio=10 # number or simulated iterations per sample
        ):
    nnd = dmat.shape[0]
    nsteps = bootstrap + step_to_sample_ratio * nsamples
    prandom=0.2
    pauto=0.6
    x = np.zeros((nsteps, nnd))
    p = np.zeros((nsteps, nnd))
    # Start the stochastic process
    p[0, :] = np.full(nnd, 0.5)
    x[0, :] = bsample(p[0, :])
    for k in range(1, nsteps):
        p[k, :] = nextprob(x[k-1, :], dmat, prandom=prandom, pauto=pauto)
        x[k, :] = bsample(p[k, :])
    # Remove the bootstrap phase
    p = p[bootstrap:, :]
    x = x[bootstrap:, :]
    # Sample random states
    idx = np.random.choice(range(len(x)), size=nsamples, replace=False)
    # idx = np.random.randint(0, len(x), size=nsamples)
    xrnd = x[idx]
    # Sample Normally distributed durations
    drnd = [nsample(state, dmat) for state in xrnd]
    # Return results
    return drnd


if __name__ == '__main__':
    dmat, nnd = readdata('inst20.txt')
    d = tspsample(dmat, nsamples=100, bootstrap=100, step_to_sample_ratio=10)
    #nsamples = x.shape[0]
    print np.asarray(d)
    np.save('../tspsamples.npy', d)


