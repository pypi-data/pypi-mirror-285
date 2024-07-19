import pandas as pd
import numpy as np
import math
from .utills import getDataFromExcel,getFromDict,interpolate_2d_array

def getSurchargeFactor(q,l,H,beta,D,T):
    file_path='Surcharge Adjustment Factor.xlsx'
    if q==0 or beta==0:
        return 1
    ts0 = getDataFromExcel(file_path,'beta=0')
    ts30 = getDataFromExcel(file_path,'beta=30')
    ts45 = getDataFromExcel(file_path,'beta=45')
    ts60 = getDataFromExcel(file_path,'beta=60')
    ts75 = getDataFromExcel(file_path,'beta=75')
    ts90 = getDataFromExcel(file_path,'beta=90') 
    
    ts_dict={
        0:ts0,
        30:ts30,
        45:ts45,
        60:ts60,
        75:ts75,
        90:ts90
    }
    d2 = getDataFromExcel(file_path,'d=2')
    d1 = getDataFromExcel(file_path,'d=1')
    d05 = getDataFromExcel(file_path,'d=0.5')
    d0 =  getDataFromExcel(file_path,'d=0')
    
    d_dict={
        2:d2,
        1:d1,
        0.5:d05,
        0:d0
    }
    if T==1:
        return getFromDict(ts_dict,beta,q/(l*H))
    else:
        if math.isinf(D/H): #??
            return 1
        elif D/H>2:
            return getFromDict(d_dict,2,q/(l*H))
        else:   
            return getFromDict(d_dict,D/H,q/(l*H))
    pass

def getSubmergenceAndSeepageFactor(Hw,Hwdash,H,beta,D,T):
    file_path='Submergence and seepage Adjustment Factor.xlsx'
    if Hw==0 and Hwdash==0:
        return 1,1
    ts0  = getDataFromExcel(file_path,'beta=0')
    ts30  = getDataFromExcel(file_path,'beta=30')
    ts45  = getDataFromExcel(file_path,'beta=45')
    ts60  = getDataFromExcel(file_path,'beta=60')
    ts90  = getDataFromExcel(file_path,'beta=90')
    ts_dict={
        0:ts0,
        30:ts30,
        45:ts45,
        60:ts60,
        90:ts90
    }
    d2 = getDataFromExcel(file_path,'d=2')
    d1 = getDataFromExcel(file_path,'d=1')
    d05 = getDataFromExcel(file_path,'d=0.5')
    d0 = getDataFromExcel(file_path,'d=0')
    d_dict={
        2:d2,
        1:d1,
        0.5:d05,
        0:d0
    }
    
    if T==1:
        return getFromDict(ts_dict,beta,Hw/H),getFromDict(ts_dict,beta,Hwdash/H)
    else:
        if math.isinf(D/H):#??
            return 1,1
        elif D/H>2:
            return getFromDict(d_dict,2,Hw/H),getFromDict(d_dict,2,Hwdash/H)
        else:   
            return getFromDict(d_dict,D/H,Hw/H),getFromDict(d_dict,D/H,Hwdash/H)

def getTensionCrackFactor(Ht,H,beta,D,T):
    file_path1='Tension Crack Adjustment Not Filled with water.xlsx'
    if Ht==0:
        return 1
    nw_ts0  =  getDataFromExcel(file_path1,'beta=0')
    nw_ts30  =  getDataFromExcel(file_path1,'beta=30')
    nw_ts45 = getDataFromExcel(file_path1,'beta=45')
    nw_ts60 = getDataFromExcel(file_path1,'beta=60')
    nw_ts75 = getDataFromExcel(file_path1,'beta=75')
    nw_ts90  = getDataFromExcel(file_path1,'beta=90')
    
    nw_ts_dict={
        0:nw_ts0,
        30:nw_ts30,
        45:nw_ts45,
        60:nw_ts60,
        75:nw_ts75,
        90:nw_ts90
    }
    nw_d1 = getDataFromExcel(file_path1,'d=1')
    nw_d05  = getDataFromExcel(file_path1,'d=0.5')
    nw_d0 = getDataFromExcel(file_path1,'d=0')
    
    nw_d_dict={
        1:nw_d1,
        0.5:nw_d05,
        0:nw_d0
    }
    file_path2='Tension Crack Adjustment Filled with water.xlsx'
    
    ww_ts0  =  getDataFromExcel(file_path2,'beta=0')
    ww_ts30  =  getDataFromExcel(file_path2,'beta=30')
    ww_ts45 = getDataFromExcel(file_path2,'beta=45')
    ww_ts60 = getDataFromExcel(file_path2,'beta=60')
    ww_ts75 = getDataFromExcel(file_path2,'beta=75')
    ww_ts90  = getDataFromExcel(file_path2,'beta=90')
    
    ww_ts_dict={
        0:ww_ts0,
        30:ww_ts30,
        45:ww_ts45,
        60:ww_ts60,
        75:ww_ts75,
        90:ww_ts90
    }
    
    ww_d1 = getDataFromExcel(file_path2,'d=1')
    ww_d05  = getDataFromExcel(file_path2,'d=0.5')
    ww_d0 = getDataFromExcel(file_path2,'d=0')
    
    ww_d_dict={
        1:ww_d1,
        0.5:ww_d05,
        0:ww_d0
    }
    
    if T==1:
        if beta==0:
            return 1
        return getFromDict(nw_ts_dict,beta,Ht/H)
    elif T==2:
        if math.isinf(D/H):
            return 1
        elif D/H>1:
            return getFromDict(nw_d_dict,1,Ht/H)
        else:   
            return getFromDict(nw_d_dict,D/H,Ht/H)
    elif T==3:
        if beta==0:
            return 1
        return getFromDict(ww_ts_dict,beta,Ht/H)
    elif T==4:
        if math.isinf(D/H):
            return 1
        elif D/H>1:
            return getFromDict(ww_d_dict,1,Ht/H)
        else:   
            return getFromDict(ww_d_dict,D/H,Ht/H)
        
def getSteadySeepageFactor(Hc,H,beta,D,T):
    data =np.array([[0,0],[0.004801913797808657, 0.002403860111599432], [0.04793204159723148, 0.06027069555169762], [0.08149318035337903, 0.09883697299431549], [0.10065438414149096, 0.12777619713975485], [0.15817283405816873, 0.20010103180179184], [0.2013203811337626, 0.2507214483547493], [0.23966020798615745, 0.30135347775848753], [0.2995883244398251, 0.37125703303275415], [0.3499242261486561, 0.43152192215906127], [0.40026593428287743, 0.4893713383229882], [0.438634793262224, 0.5279260029148256], [0.4985803289920626, 0.5905831393019516], [0.5561394238864728, 0.6459996632273275], [0.599310196663628, 0.6869581879307642], [0.6472944960893725, 0.7254896268210402], [0.7000807093129257, 0.7664249258229157], [0.7432863206424228, 0.7928906127520716], [0.7912822329189481, 0.8265911057175872], [0.8392839516208637, 0.8578761257207227], [0.8776992620033328, 0.8771070066135187], [0.8968953043437867, 0.891553392984677], [0.935328034002427, 0.9035378549903325], [0.9713510971240775, 0.9179435963837584], [1, 0.9275416175539853]])
    hwdash = H*(interpolate_2d_array(data,Hc/H))
    a,b = getSubmergenceAndSeepageFactor(0,hwdash,H,beta,D,T)
    return hwdash,b
