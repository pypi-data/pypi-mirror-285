"""
Calculation of :
1) resolution
"""


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import numpy as np
from scipy.stats import f_oneway
import copy
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def resolution(data_y,significance_level):

    #initialization:
    ySour = copy.deepcopy(data_y)
    alpha = significance_level
    Reso = None

    # Main Resolution: 
    y_mean = np.mean(ySour, axis=1)
    y_mean_new  = y_mean.reshape(ySour.shape[0], 1)
    

    sy = np.sort(y_mean_new, axis=None) # Order from smallest to largest
    dsy = np.diff(sy) # Diferncia consecutiva
    odsy = np.sort(dsy, axis=None) # dsy Order from smallest to largest


    i=0    
    for x in odsy:
        indexmin=np.where(dsy == odsy[i])[0]
        a=ySour[np.where(y_mean_new == sy[indexmin])[0],:].T.tolist()
        b=ySour[np.where(y_mean_new == sy[indexmin+1])[0],:].T.tolist()
        i=i+1
        if f_oneway(a, b).pvalue<alpha:
            Reso=odsy[i-1]            
            break

    return Reso