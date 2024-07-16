# -*- coding: utf-8 -*-
"""Methods for feature extraction and preprocessing util_feature: input/output is pandas
Docs::




"""
import os, sys, copy, re, numpy as np, pandas as pd
from collections import OrderedDict
#############################################################################################
from utilmy import log, log2, log3
verbosity = 5

log2("os.getcwd", os.getcwd())


#############################################################################################
def gini_coefficient(x):
    """Compute Gini coefficient of array of values
       Dispersion of a list

    """
    diffsum = 0
    for i, xi in enumerate(x[:-1], 1):
        diffsum += np.sum(np.abs(xi - x[i:]))
    return diffsum / (len(x)**2 * np.mean(x))




