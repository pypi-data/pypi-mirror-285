# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 15:09:19 2024

@author: ThinkPad
"""
import os
dirpath=os.path.dirname(__file__)
import sys
sys.path.append(os.path.join(dirpath,'../..'))

import pandas
from scient.cluster import fourstep

#3d
x=pandas.read_csv('../test/data/3d_guassian_mix.csv')
clm=fourstep.FourStep(plot=True)
clm.fit(x.values)
#2d
x=pandas.read_csv('../test/data/3d_guassian_mix.csv')
clm=fourstep.FourStep(plot=True)
clm.fit(x.values[:,:2])
#1d
x=pandas.read_csv('../test/data/3d_guassian_mix.csv')
clm=fourstep.FourStep(plot=True)
clm.fit(x.values[:,:1])

