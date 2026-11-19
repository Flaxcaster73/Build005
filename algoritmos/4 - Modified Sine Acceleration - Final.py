# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 11:10:36 2025

CAM Development project

SVAJ Equations: Modified Sine Acceleration - Full

@author: JMG
"""

import numpy as np
import math
import matplotlib as mpl
import matplotlib.pyplot as plt

""" Defining variables 

h       = Total follower linear displacement, mm
Theta   = Current angular displacement, rad
Beta    = Total angular displacement to achieve h or a dwell, rad

"""

# Assigning values

h = 25.4
Beta_deg = 90

Beta_rad = Beta_deg*(math.pi/180)

""" Uprise """

# Preallocating space for vectors

s_1 = np.zeros((91,1))
v_1 = np.zeros((91,1))
a_1 = np.zeros((91,1))
j_1 = np.zeros((91,1))

# Creating vectors for each value of Theta

for ii in range(0,91):
    
    Theta_deg = ii 
    Theta_rad = Theta_deg*(math.pi/180)
    
    CC = (h/Beta_rad**2)*((4*math.pi**2)/(math.pi+4))
    
    if Theta_rad >= 0 and Theta_rad <= Beta_rad/8:
        
        # Region 1
        
        Argument = 4*math.pi*Theta_rad/Beta_rad
        
        s_1[ii,0] = CC*(Beta_rad/(4*math.pi))*(Theta_rad-(Beta_rad/(4*math.pi))*np.sin(Argument))
        
        v_1[ii,0] = CC*(Beta_rad/(4*math.pi))*(1-np.cos(Argument))
        
        a_1[ii,0] = CC*np.sin(Argument)
        
        j_1[ii,0] = CC*(4*math.pi/Beta_rad)*np.cos(Argument)
 
    elif Theta_rad > Beta_rad/8 and Theta_rad <= 7*Beta_rad/8:
        
        # Region 2
        
        Argument = (4*math.pi*Theta_rad/(3*Beta_rad))-(math.pi/6)
        
        s_1[ii,0] = (CC*Beta_rad/(2*math.pi))*((Theta_rad/2)+(Beta_rad/math.pi)-(9*Beta_rad/(8*math.pi))*np.cos(Argument))
        
        v_1[ii,0] = (CC*Beta_rad/(4*math.pi))*(1+3*np.sin(Argument))
        
        a_1[ii,0] = CC*np.cos(Argument)
        
        j_1[ii,0] = -1*CC*(4*math.pi/(3*Beta_rad))*np.sin(Argument)

    else:         
        
        # Region 3
        
        Argument = (4*math.pi*Theta_rad/Beta_rad)-2*math.pi
        
        s_1[ii,0] = (CC*Beta_rad/math.pi)*((Theta_rad/4)+(Beta_rad/math.pi)-(Beta_rad/(16*math.pi))*np.sin(Argument))
        
        v_1[ii,0] = (CC*Beta_rad/(4*math.pi))*(1-np.cos(Argument))
        
        a_1[ii,0] = CC*np.sin(Argument)
        
        j_1[ii,0] = CC*(4*math.pi/Beta_rad)*np.cos(Argument)

""" Dwell """

# Preallocating space for vectors

s_2 = np.ones((91,1))
v_2 = np.zeros((91,1))
a_2 = np.zeros((91,1))
j_2 = np.zeros((91,1))

s_2 = h*s_2

""" Downfall """

# Preallocating space for vectors

s_3 = np.zeros((91,1))
v_3 = np.zeros((91,1))
a_3 = np.zeros((91,1))
j_3 = np.zeros((91,1))

s_3 = h - s_1
v_3 = -1*v_1
a_3 = -1*a_1
j_3 = -1*j_1

 
""" Dwell """

# Preallocating space for vectors

s_4 = np.zeros((91,1))
v_4 = np.zeros((91,1))
a_4 = np.zeros((91,1))
j_4 = np.zeros((91,1))

""" Arranging full vectors """

s = np.vstack((s_1[0:91,:],s_2[0:89,:],s_3[0:91,:],s_4[0:90,:]))

v = np.vstack((v_1[0:91,:],v_2[0:89,:],v_3[0:91,:],v_4[0:90,:]))

a = np.vstack((a_1[0:91,:],a_2[0:89,:],a_3[0:91,:],a_4[0:90,:]))

j = np.vstack((j_1[0:91,:],j_2[0:89,:],j_3[0:91,:],j_4[0:90,:]))

""" Maximum & Minimum values of VAJ """

Max_Velocity = np.max(v)
Max_Acceleration = np.max(a)
Max_Jerk = np.max(j)

Min_Velocity = np.min(v)
Min_Acceleration = np.min(a)
Min_Jerk = np.min(j)

print('Max_Velocity: ', Max_Velocity)
print('Min_Velocity: ', Min_Velocity)
print('Max_Acceleration: ', Max_Acceleration)
print('Min_Acceleration: ', Min_Acceleration)
print('Max_Jerk: ', Max_Jerk)
print('Min_Jerk: ', Min_Jerk)

""" Plotting functions """ 

Th_1 = np.arange(0,91)
Th_2 = np.arange(90,181)
Th_3 = np.arange(180,271)
Th_4 = np.arange(270,361)

# Creating one Figure and three Axes instances, the easy way...
# using plt.subplots(). The first two numbers indicate the size
# of the grid: four rows and one column of different plots, i.e.,
# four windows

fig,ax = plt.subplots(4,1,figsize=(15,15))

# Applying Axes object methods for plotting, specifying line properties
# through keywords, i.e., lw=linewidth, ls=linestyle, color, etc.
# Also, see how different plots in the grid are indexed

ax[0].plot(Th_1,s_1,Th_2,s_2,Th_3,s_3,Th_4,s_4,color='black',lw=1,ls='-')
ax[1].plot(Th_1,v_1,Th_2,v_2,Th_3,v_3,Th_4,v_4,color='black',lw=1,ls='-')
ax[2].plot(Th_1,a_1,Th_2,a_2,Th_3,a_3,Th_4,a_4,color='black',lw=1,ls='-')
ax[3].plot(Th_1,j_1,Th_2,j_2,Th_3,j_3,Th_4,j_4,color='black',lw=1,ls='-')

# Specifying number of ticks per axis

ax[0].xaxis.set_major_locator(mpl.ticker.MaxNLocator(20))
ax[0].yaxis.set_major_locator(mpl.ticker.MaxNLocator(10))
ax[0].xaxis.set_minor_locator(mpl.ticker.MaxNLocator(40))

ax[1].xaxis.set_major_locator(mpl.ticker.MaxNLocator(20))
ax[1].yaxis.set_major_locator(mpl.ticker.MaxNLocator(10))
ax[1].xaxis.set_minor_locator(mpl.ticker.MaxNLocator(40))

ax[2].xaxis.set_major_locator(mpl.ticker.MaxNLocator(20))
ax[2].yaxis.set_major_locator(mpl.ticker.MaxNLocator(10))
ax[2].xaxis.set_minor_locator(mpl.ticker.MaxNLocator(40))

ax[3].xaxis.set_major_locator(mpl.ticker.MaxNLocator(20))
ax[3].yaxis.set_major_locator(mpl.ticker.MaxNLocator(10))
ax[3].xaxis.set_minor_locator(mpl.ticker.MaxNLocator(40))

# Setting grids

ax[0].grid(color="black",which="both",ls=":",lw=0.25)
ax[1].grid(color="black",which="both",ls=":",lw=0.25)
ax[2].grid(color="black",which="both",ls=":",lw=0.25)
ax[3].grid(color="black",which="both",ls=":",lw=0.25)

# Figure title

fig.suptitle('SVAJ functions: Modified Sine Acceleration',fontsize=15,fontname="serif",
             color="black") 

# Setting titles for each axis

ax[0].set_xlabel("Theta")
ax[0].set_ylabel("S")
ax[1].set_xlabel("Theta")
ax[1].set_ylabel("V")
ax[2].set_xlabel("Theta")
ax[2].set_ylabel("A")
ax[3].set_xlabel("Theta")
ax[3].set_ylabel("J")

# Saving figure

fig.savefig("z - Modified Sine Acceleration",dpi=400,facecolor="#f1f1f1")


""" Exporting data to Excel """

import pandas as pd

# Sheet 1: Maximum & Minimum values of VAJ

Resumen = pd.DataFrame({
    'Parameter': ['Max_Velocity','Min_Velocity','Max_Acceleration',
                  'Min_Acceleration','Max_Jerk','Min_Jerk'],
    'Value': [Max_Velocity,Min_Velocity,Max_Acceleration,
              Min_Acceleration,Max_Jerk,Min_Jerk],
    'Units': ['(mm/rad)','(mm/rad)','(mm/rad²)',
              '(mm/rad²)','(mm/rad³)','(mm/rad³)']})

# Sheet 2: Full SVAJ vectors for each degree of Theta

Datos = pd.DataFrame({
    'Theta (deg)': np.arange(0,s.shape[0]),
    'S (mm)': s[:,0],
    'V (mm/rad)': v[:,0],
    'A (mm/rad²)': a[:,0],
    'J (mm/rad³)': j[:,0]})

# Saving Excel file

with pd.ExcelWriter("z - Modified Sine Acceleration.xlsx") as writer:
    Resumen.to_excel(writer,sheet_name='Max_Min',index=False)
    Datos.to_excel(writer,sheet_name='SVAJ',index=False)
