# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 14:23:08 2024

@author: Peter
"""
#from . import __flatchain__,__rng__
import numpy as np

from pathlib import Path



rng = np.random.default_rng()

chainpath=Path(__file__).parent/ 'chain4b.txt'
flatchain=np.genfromtxt(chainpath.open())

__all__=["get_Rsamp"]


#print("haha")

def MRddo(m,rho):
    a= -0.492
    mu = np.sqrt(1-m)
    mu2=1-m
    c=0.8284271247461903
    return 1+mu*(a+c*rho) + mu2*(-2.-np.sqrt(2)*a+c*rho)



def get_Rsamp(M,Nsamp=1):
     sel=flatchain[:,3]>M
     chain_sel=rng.choice(flatchain[sel],size=Nsamp)

     Rs=chain_sel[:,4]*MRddo(M/chain_sel[:,3],chain_sel[:,2])
     return Rs
 