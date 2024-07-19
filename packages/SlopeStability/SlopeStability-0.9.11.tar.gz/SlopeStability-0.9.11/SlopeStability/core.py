# my_package/core.py
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from .utills import getDataFromExcel,getFromDict,interpolate_2d_array,FailureCircle
from .adjustment_factor import getSubmergenceAndSeepageFactor,getSurchargeFactor,getSteadySeepageFactor,getTensionCrackFactor

def PURELY_COHESIVE_SOIL(beta,H,Hw,Hwdash,D,c,lw,l,Ht,q):
    file_path='PHI=0.xlsx'
    toe_circle = getDataFromExcel(file_path,'Toe_circle')
    d_0 = getDataFromExcel(file_path,'d=0')
    d_01 = getDataFromExcel(file_path,'d=0.1')
    d_02 = getDataFromExcel(file_path,'d=0.2')
    d_03 = getDataFromExcel(file_path,'d=0.3')
    d_05 = getDataFromExcel(file_path,'d=0.5')
    d_1 = getDataFromExcel(file_path,'d=1')
    d_105 = getDataFromExcel(file_path,'d=1.5')
    d_2 = getDataFromExcel(file_path,'d=2')
    d_3 = getDataFromExcel(file_path,'d=3')
    d_inf=5.641

    my_dict={
        0:d_0,
        0.1:d_01,
        0.2:d_02,
        0.3:d_03,
        0.5:d_05,
        1:d_1,
        1.5:d_105,
        2:d_2,
        3:d_3
    }

    x0_all=getDataFromExcel(file_path,'x_all_circle')
    x0_d05=getDataFromExcel(file_path,'x_d=0.5')
    x0_d0=getDataFromExcel(file_path,'x_d=0')

    x0_dict={
        0:x0_d0,
        0.5:x0_d05
    }

    y0_toe=getDataFromExcel(file_path,'y_toe_circle')
    y0_d0=getDataFromExcel(file_path,'y_d=0')
    y0_d1=getDataFromExcel(file_path,'y_d=1')
    y0_d2=getDataFromExcel(file_path,'y_d=2')
    y0_d3=getDataFromExcel(file_path,'y_d=3')

    y0_dict={
        0:y0_d0,
        1:y0_d1,
        2:y0_d2,
        3:y0_d3
    }
    
    #Deep Circle
    uq1 = getSurchargeFactor(q,l,H,beta,D,2)# Surcharge adjustment factor
    uw1,uwdash1 = getSubmergenceAndSeepageFactor(Hw,Hwdash,H,beta,D,2) # Submergence and seepage adjustment factor
    ut1 = getTensionCrackFactor(Ht,H,beta,D,2)  # Tension Crack adjustment factor

    d = D/H
    N1=0
    if d>3:
        N1=getFromDict(my_dict,3,beta)
    else:
        N1 = getFromDict(my_dict,d,beta)
    Pd1 = ((l*H+q)-(lw*Hw))/(uq1*uw1*ut1)
#     print('Stability Number: ',N1)
#     print('Surcharge Factor: ',uq1)
#     print('Submergence and seepage Factor: ',uw1)
#     print('Tension Crack Factor: ',ut1)
    FOS1 = N1*c/Pd1
#     print('Factor of safety For Deep circle: ',FOS1)

    if d>0.5:
        x01=H*interpolate_2d_array(x0_all,beta)
    else:
        x01=H*getFromDict(x0_dict,D/H,beta)
    if d>3:
        y01=H*getFromDict(y0_dict,3,beta)
    else:
        y01=H*getFromDict(y0_dict,D/H,beta)

    #Toe Circle
    uq2 = getSurchargeFactor(q,l,H,beta,D,1)# Surcharge adjustment factor
    uw2,uwdash2 = getSubmergenceAndSeepageFactor(Hw,Hwdash,H,beta,D,1) # Submergence and seepage adjustment factor
    ut2 = getTensionCrackFactor(Ht,H,beta,D,1)  # Tension Crack adjustment factor

    d = D/H
    
    N2 = interpolate_2d_array(toe_circle,beta)

    Pd2 = ((l*H+q)-(lw*Hw))/(uq2*uw2*ut2)
#     print('Stability Number: ',N2)
#     print('Surcharge Factor: ',uq2)
#     print('Submergence and seepage Factor: ',uw2)
#     print('Tension Crack Factor: ',ut2)
    # print(Pd)
    FOS2 = N2*c/Pd2
#     print('Factor of safety For Deep circle: ',FOS2)

    x02=H*interpolate_2d_array(x0_all,beta)
    y02=H*interpolate_2d_array(y0_toe,beta)
    
    if FOS1<FOS2:
        print('Factor of safety For Deep circle: ',FOS1)
        print('X0 = ',x01)
        print('Y0 = ',y01)
        R=y01+D
        print('Radius of slipe circle = ',R)
        FailureCircle(x01,y01,D,H,beta,2,q,Hw)
        return [FOS1,x01,y01,R]
    else:
        print('Factor of safety For Toe circle: ',FOS2)
        print('X0 = ',x02)
        print('Y0 = ',y02)
        R= np.sqrt(x02*x02+y02*y02)
        print('Radius of slipe circle = ',R)
        FailureCircle(x02,y02,D,H,beta,1,q,Hw)
        return [FOS2,x02,y02,R]
    
    pass

def CHI_PHI_SOIL(beta,H,Hw,Hc,Hwdash,c,phi,l,lw,q,Ht):
    file_path='PHI,C.xlsx'
    lcf0 = getDataFromExcel(file_path,'lcf=0')
    lcf05 = getDataFromExcel(file_path,'lcf=0.5')
    lcf1 = getDataFromExcel(file_path,'lcf=1')
    lcf105 = getDataFromExcel(file_path,'lcf=1.5')
    lcf2 = getDataFromExcel(file_path,'lcf=2')
    lcf3 = getDataFromExcel(file_path,'lcf=3')
    lcf4 = getDataFromExcel(file_path,'lcf=4')
    lcf5 = getDataFromExcel(file_path,'lcf=5')
    lcf6 = getDataFromExcel(file_path,'lcf=6')
    lcf7 = getDataFromExcel(file_path,'lcf=7')
    lcf8 = getDataFromExcel(file_path,'lcf=8')
    lcf10 = getDataFromExcel(file_path,'lcf=10')
    lcf15 = getDataFromExcel(file_path,'lcf=15')
    lcf20 = getDataFromExcel(file_path,'lcf=20')
    lcf30 = getDataFromExcel(file_path,'lcf=30')
    lcf50 = getDataFromExcel(file_path,'lcf=50')
    lcf100 = getDataFromExcel(file_path,'lcf1=100')

    lcf_dict={
        0:lcf0,
        0.5:lcf05,
        1:lcf1,
        1.5:lcf105,
        2:lcf2,
        3:lcf3,
        4:lcf4,
        5:lcf5,
        6:lcf6,
        7:lcf7,
        8:lcf8,
        10:lcf10,
        15:lcf15,
        20:lcf20,
        30:lcf30,
        50:lcf50,
        100:lcf100
    }

    xlcf0=getDataFromExcel(file_path,'x_lcf=0')
    xlcf2=getDataFromExcel(file_path,'x_lcf=2')
    xlcf5=getDataFromExcel(file_path,'x_lcf=5')
    xlcf10=getDataFromExcel(file_path,'x_lcf=10')
    xlcf20=getDataFromExcel(file_path,'x_lcf=20')
    xlcf100=getDataFromExcel(file_path,'x_lcf=100')

    xlcf_dict={
        0:xlcf0,
        2:xlcf2,
        5:xlcf5,
        10:xlcf10,
        20:xlcf20,
        100:xlcf100,
    }

    ylcf0=getDataFromExcel(file_path,'y_lcf=0')
    ylcf2=getDataFromExcel(file_path,'y_lcf=2')
    ylcf5=getDataFromExcel(file_path,'y_lcf=5')
    ylcf10=getDataFromExcel(file_path,'y_lcf=10')
    ylcf20=getDataFromExcel(file_path,'y_lcf=20')
    ylcf100=getDataFromExcel(file_path,'y_lcf=100')

    ylcf_dict={
        0:ylcf0,
        2:ylcf2,
        5:ylcf5,
        10:ylcf10,
        20:ylcf20,
        100:ylcf100,
    }
    uq = getSurchargeFactor(q,l,H,beta,0,1)# Surcharge adjustment factor
    uw,uwdash = getSubmergenceAndSeepageFactor(Hw,Hwdash,H,beta,0,1) # Submergence and seepage adjustment factor
    ut = getTensionCrackFactor(Ht,H,beta,0,1)  # Tension Crack adjustment factor

    Pd = ((l*H+q)-(lw*Hw))/(uq*uw*ut)
    # print(uw)
    # print(Pd)

    if Hc!=0:
        Hwdash,uwdash=getSteadySeepageFactor(Hc,H,beta,0,1)

    Pe = ((l*H+q)-(lw*Hwdash))/(uq*uwdash)
    # print(Pe)
    # print(uw)
    # print(uwdash)

    lcf=Pe*(np.tan(np.radians(phi))/c)

    Ncf=getFromDict(lcf_dict,lcf,1/np.tan(np.radians(beta)))
    FOS = Ncf*(c/Pd)
    print('Factor of safety For phi>0 and c>0: ',FOS)#1

    x0=H*getFromDict(xlcf_dict,lcf,1/np.tan(np.radians(beta)))
    y0=H*getFromDict(ylcf_dict,lcf,1/np.tan(np.radians(beta)))
    print('x0 = ',x0)
    print('y0 = ',y0)
    FailureCircle(x0,y0,0,H,beta,1,q,Hw)
    R= np.sqrt(x0*x0+y0*y0)
    print('Radius of slip circle = ',R)
    return [FOS,x0,y0,R]

    pass

def INFINITE_SLOPE(beta,theeta,H,c,phi,cdash,phdash,l,lw,X,T):
    file_path='B.xlsx'
    Bru = getDataFromExcel(file_path,'B')
    beta=np.radians(beta)
    theeta=np.radians(theeta)
    phdash=np.radians(phdash)
    #Factorh Of Safety Determination
    if theeta==beta:
        ru = (X*lw* (np.cos(beta))**2)/(T*l)
    else:
        ru = lw/(l*(1+np.tan(beta)*np.tan(theeta)))

    A=1-ru*(1+(np.tan(beta))**2)
    B=interpolate_2d_array(Bru,1/np.tan(beta))

    FOS1 = A*(np.tan(phdash)/np.tan(beta))+B*(cdash/(l*H))#Effective stress analyses
    FOS2 = (np.tan(phi)/np.tan(beta))+B*(c/(l*H))#Total stress analyses

    print('Factor of safety for infinite slope condition: ',max(FOS1,FOS2))#1.63
    return [max(FOS1,FOS2)]

    pass

def PURELY_COHESIVE_SOIL_WITH_INCREASING_SHEAR_STRENGTH(beta,H,H0,Cb,l,lb):
    file_path='Phi_0_Increasing_shear_strength.xlsx'
    m0 = getDataFromExcel(file_path,'m=0')
    m25= getDataFromExcel(file_path,'m=0.25')
    m50= getDataFromExcel(file_path,'m=0.5')
    m75= getDataFromExcel(file_path,'m=0.75')
    m100=getDataFromExcel(file_path,'m=1')
    m125=getDataFromExcel(file_path,'m=1.25')
    m150=getDataFromExcel(file_path,'m=1.5')
    m175=getDataFromExcel(file_path,'m=1.75')
    m200=getDataFromExcel(file_path,'m=2')

    m_dict={
        0:m0,
        0.25:m25,
        0.5:m50,
        0.75:m75,
        1:m100,
        1.25:m125,
        1.5:m150,
        1.75:m175,
        2:m200
    }
    M=H0/H
    N = getFromDict(m_dict,M,beta)
    # print(N)
    FOS = N*(Cb/(lb*(H+H0)))# For submerge slope
    print('Factor of safety for Phi=0,Increasing Shear Strength: ',FOS)#1.36
    return [FOS]
    pass
