#%%
# from scipy import optimize
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import expm
from qutip import *
from TK_basics import *
start_time = time.time()#checking how long the code takes

D = 25#dimension the density matrix to reconstruct

'''
List of displacement points, at least D^2-1.
Let's reconstruct this list for a grid-based CF.
Note that the order has to be the same as when we arrange
our observables from experiments for reconstruction later!!
'''
# al = np.linspace(-8.5,8.5,51)
# al = np.linspace(-11,11,61)#cdim180
# al = np.linspace(-7.5,7.5,51)

#Clara's experiments plus
left = np.linspace(-8.5, -4.6, 20)
middle = np.linspace(-4.5, 4.5, 41)#fixed
right = np.linspace(4.6, 8.5, 20)
al = np.concatenate([left, middle, right])

al_rev = np.flip(al)
AL = []
for m in range(len(al_rev)):
    for n in range(len(al)):
        AL.append(al[n]+1j*al_rev[m])
AL = np.array(AL)
'''
This ordering corresponds to starting at the top left corner
of CF phase space, then go right, sweeping the real part first
'''
n_dis = len(AL)
    
RM = 2*n_dis #no of observables, factor of 2 as we have real and imaginary CF
nD = D**2-1 #no of real parameters for general state
Ntr = D**2 #no of training for obtaining the map, at least D^2

cdim =130 #truncation dimension in simulation
a = destroy(cdim).full() #annihilation for cavity

#construct displacements
Dis = np.zeros([len(AL),cdim,cdim], dtype=np.complex128)
for i in range(len(AL)):
    Dis[i] = expm(AL[i]*a.T.conj()-np.conjugate(AL[i])*a)

#this part if for obtaining the map
X_r = np.zeros([RM + 1, Ntr], dtype=np.complex128) #store readouts
X_r[0,:] = np.ones([1, Ntr]) #setting the ones
Y_r = np.zeros([nD, Ntr], dtype=np.complex128) #store the targets
for j in np.arange(0, Ntr):
    #qudit mixed state embedded in the cavity mode
    rd1 = np.zeros([cdim, cdim], dtype = np.complex128)
    u_rand = rand_ket(D)
    r_rand = (u_rand*u_rand.dag()).full()
    rd1[0:D,0:D] = r_rand#randRho(D)

    #element-wise column-stacking parametrisation
    # Y_r[:, j] = np.transpose(r_rand).reshape((D**2))

    #Reimdiag parametrisation
    cw = 0
    #diagonal elements
    for j1 in np.arange(0, D-1):
        Y_r[cw, j] = rd1[j1, j1].real
        cw += 1
    #off-diagonal elements
    for j1 in np.arange(0, D-1):
        for j2 in np.arange(j1+1, D):
            Y_r[cw, j] = rd1[j1, j2].real
            cw += 1
            Y_r[cw, j] = rd1[j1, j2].imag
            cw += 1
    
    CF_re = np.zeros(n_dis, dtype=np.complex128)
    CF_im = np.zeros(n_dis, dtype=np.complex128)
    w = 0
    for v in np.arange(0, n_dis):
        oo = np.trace(rd1@Dis[v])
        CF_re[w] = oo.real
        CF_im[w] = oo.imag
        w += 1
    X_r[1:n_dis+1, j] = CF_re
    X_r[n_dis+1:, j] = CF_im

'''
So essentially, X_r contains the observables. 
First element is 1, and the rest we stack the real and imaginary parts
of the CF.
'''

#ridge regression
lamb = 0 #zero for linear regression

#training, now to obtain the map
X_R = np.zeros([nD + 1, Ntr], dtype=np.complex128) #will contain the parameters
X_R[0,:] = np.ones([1, Ntr]) #setting the ones
Y_R = np.zeros([RM, Ntr], dtype=np.complex128) #will contain the obs

#re-defining variables
X_R[1:nD+1,:] = Y_r
Y_R[:,:] = X_r[1:RM+1,:]

Error, beta = QN_regression(X_R, Y_R, lamb)
'''
beta here contains both the constant vector v and map M
beta = [v M]
'''

M = beta[:,1:nD+1] #the map
W = np.matmul(np.linalg.inv(np.matmul(np.transpose(M),M)),np.transpose(M))
eta = np.linalg.norm(M,2)*np.linalg.norm(W,2)#the condition number
print(f'Error is {Error}')
print(f'CN is {eta}')

print("")
print("--- %s seconds ---" % (time.time() - start_time))

#now save
import os
# os.chdir("/Users/tanjungkrisnanda/Library/CloudStorage/Dropbox/PY/20260121_Tomography")
os.chdir(r"C:\Users\tanju\Dropbox\PY\20260121_Tomography")
np.savez(f"map_ideal_D{D}_reimdiag_CF1mode_grid.npz", 
         M = M, W = W, beta = beta, CN = eta)
