# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 14:22:39 2024

@author: Peter
"""



#chainpath=Path(__file__).parent/ 'chain4b.txt'




#global __flatchain__
#
#__flatchain__=np.genfromtxt(chainpath.open())

#from .ddomsamp import *



from .ddomsamp import get_Rsamp

__all__=["get_Rsamp"]