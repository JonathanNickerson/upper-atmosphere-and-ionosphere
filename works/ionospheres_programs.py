# -*- coding: utf-8 -*-

"""
Created on Mon Jan 23 19:41:05 2012
@author: Jonathan Nickerson
"""

# Importing everything python needs in order to be smart.
import numpy as np                                      # Numpy tells python how to work with numbers.
import matplotlib.pyplot as plt                         # Matplotlib tells python how to make pretty plots.

#***********************************************************************
# Declaring some global variables.                                     *
#***********************************************************************

# Creating a list of all of the neutral species that live in our virtual 
# thermosphere so that we can later assign properties to them.
neutrals = ['O','N','O2','N2','NO']

#Creating a list of all of the ion species tht live in our virtual
#thermosphere so that we can later assign properties to them.
ions = ['O+', 'N+', 'O2+', 'N2+']

#***********************************************************************
# A shit ton of custom definitions.                                    *
#***********************************************************************

def calculate_average_scale_height(n_base, m, H, rho_tot):    
    # Calculating an average (mass density weighted) scale height for the 
    # thermosphere. Instructing python to assign the average scale height to all of 
    # the species from the base, z(0), up to an altitude of 120km, z(29).
    H_ave = np.zeros(29.0)
    for i in range (0, 29):
        H_ave[i] = (n_base['O']*m['O']*H['O'][i] + 
                    n_base['N']*m['N']*H['N'][i] + 
                    n_base['O2']*m['O2']*H['O2'][i] + 
                    n_base['N2']*m['N2']*H['N2'][i] + 
                    n_base['NO']*m['NO']*H['NO'][i])/rho_tot    

        H['O'][i] = H_ave[i]
        H['N'][i] = H_ave[i]
        H['O2'][i] = H_ave[i]
        H['N2'][i] = H_ave[i]
        H['NO'][i] = H_ave[i]
    return H_ave

def read_solar_flux():    
    """
    Example:
    import ionospheres_programs as ip
    
    then call as a function:    
    data = ip.read_solar_flux()
    
    This definition asks python to read the text document line by line and 
    searches for the given strings. Each given string is also assigned a key. 
    Once python finds the first string it reads the line directly below it. 
    It Associates that line to the corresponding key. It then places that 
    string into the dictionary called data, splits that line up into individual 
    'words/values', and changes it to type float.  
    """      
    f = open("/Users/jsni/Desktop/Ionospheres Assignments/solar_flux.txt", 
             'r')
    lines=f.readlines()
    var={'lower':'Wavelength Lower (A)\n',
         'upper':'Wavelength Upper (A)\n',
         'F74113':'F74113\n',
         'Abi':'Abi\n',
         'N2':'N2 abs\n',
         'N2+':'N2->N2+\n',
         'N2_Np':'N2->N+\n',
         'O2':'O2 abs\n',
         'O2+':'O2->O2+\n',
         'O2_Op':'O2->O+\n',
         'O4S':'O->O+(4S)\n',
         'O2D':'O->O+(2D)\n',
         'O2P':'O->O+(2P)\n',
         'O':'O abs\n',
         'N_Np':'N->N+\n',
         'N':'N abs\n'}
    data={}
    for k in var.keys():
        line=lines[1+lines.index(var[k])]
        data[k]=np.array(line.split(), dtype=float)
    
    # Assigning an empty array for NO as a place holder.
    data['NO'] = np.zeros(37)
    
    # Summing up the various O+ souces to get the total amount of O+
    data['O+'] = data['O4S'] + 2*data['O2_Op'] + data['O2D'] + data['O2P']
    
    # Summing up the various N+ souces to get the total amount of N+
    data['N+'] = 2*data['N2_Np'] + data['N_Np']
    
    # The absorption cross section values for each species in the table 
    # are presented in units of [Mb]; to transform them to [cm^2] multiply by 1E-18.
    # Multiply by 1E-4 to convert from [cm^2] to [m^2].
    for s in neutrals:
        data[s] *= 1E-18*1E-4
    for i in ions:
        data[i] *=  1E-18*1E-4
    return data

def calculate_number_densities(T, z, H, n_base):
    # Creating an empty dictionary to store our number density arrays.
    n = {}        
    # Creating an empty array for each species, s, and setting the first value in 
    # those arrays to the corresponding initial number densities.
    # Calculating the value of number density for each species at every step in 
    # altitude and storing that value. In other words we are calculating number 
    # density as a function of z, n(z), in [m^-3].
#    for s in species:
#        n[s] = np.zeros(1000.0)
#        n[s][0] = n_base[s]
#        for i in range(1, 1000):
#            n[s][i] = n[s][i-1]*(1 - (k*(T[i]-T[i-1]) + m[s]*g[i](z[i]-z[i-1]))/(k*T[i]))   
    for s in neutrals:
        n[s] = np.zeros(1000.0)
        n[s][0] = n_base[s]
        for i in range(1, 1000):
            n[s][i] = (n[s][i-1]*T[i-1])/(T[i])*np.exp(-(z[i]-z[i-1])/H[s][i])        
    return n

def calculate_column_densities(n, H, z):    
    # Creating an empty dictionary to store our column density arrays.
    col_n = {}
    # Integrating the number densities multiplied by the difference in altitude 
    # from the top of the atmosphere down. Then storing the values of the integrals 
    # at each altitude. This is how to calculate the column density of each species.
    # Creating an empty array for each species, s, and setting the last value in 
    # those arrays to the number density multiplied by the scale height at the top 
    # of the atmosphere. We use this as our initual value to get the integration 
    # started. We then iterate in reverse over the range of values in our matrix 
    # excluding the value that we have already stored.
    for s in neutrals:
        col_n[s] = np.zeros(1000.0)
        col_n[s][999] = n[s][999]*H[s][999]    
        for i in reversed(range(0, 999)):
            col_n[s][i] = n[s][i]*(z[i+1] - z[i]) + col_n[s][i+1]    
    return col_n

def calculate_optical_depth(data, col_n, ztop):
    # Creating an empty dictionary to store our optical depth arrays.
    tau = {}
    # Calculating the optical depth as a function of altitude, wavelength, and 
    # zenith angle. In our model we will assume zenith angle of 0 (ie the sun is 
    # directly overhead). This simplifies the calculation since we won't have to 
    # concern ourselves with the secant term. Thus our optical depth will only be a 
    # function of altitude and wavelength. We muse set the size of the array being
    # cautious since the wavelength arrays and number density arrays are of 
    # different sizes.
    for s in neutrals:
        tau[s] = np.zeros((1000.0,37.0))
#        for i in range(0,1000):
#            for j in range(0,37):
#                tau[s][i][j] = data[s][j]*col_n[s][i]    
        for j in range(0,37):
            tau[s][0:ztop,j] = data[s][j]*col_n[s][0:ztop]
    return tau

def combine_optical_depths(tau, sza):
    # To get an intensity profile for the atmosphere as a whole (all species) we sum 
    # all of the optical depths together. In othr words this will give us the true 
    # optical depth for each of the 37 frequencies as they penetrate into an atmosphere 
    # of mixed species. Whereas before we were calculating how each species individually 
    # affects each wavelength.
    sumtau = np.zeros((1000.0,37.0))
    for s in neutrals:
        sumtau += tau[s]*(1/sza)
    return sumtau

def calculate_inensity(I_inf, sumtau, ztop):
    # Calculating the intensity as it varies with depth from the top of the 
    # atmosphere down.
    I = np.zeros((1000.0,37.0))
#    for i in range (0, 1000):
#        for j in range(0,37):
#            I[i][j] = I_inf[j]*np.exp(-sumtau[i][j])
    for j in range(0,37):
        I[0:ztop,j] = I_inf[j]*np.exp(-sumtau[0:ztop,j])
    return I

def calculate_energy_dissipation(eps, n, data, I, e, ztop):
    # Creating an empty dictionary to fill using numpy and calculated Q values
    Q = {}
    # All of the work we do calculating optical depth and intensity is so that we 
    # can calculate the energy dissipation (heating) as a function of altitude in units 
    # of [watts/m^3]. Playing the same game as before: 
    for s in neutrals:
        Q[s] = np.zeros(1000.0)
#        for i in range(0, 1000):
#            for j in range(0, 37):
#                Q[s][i] += eps*n[s][i]*data[s][j]*I[i][j]*e[j]
        for j in range(0, 37):
            Q[s][0:ztop] += eps*n[s][0:ztop]*data[s][j]*I[0:ztop,j]*e[j]
    return Q

def combine_energy_dissipation(Q):
    # To calculate the TOTAL heting over all wavelengths for all species we must sum
    # all of our Q's together.
    sumQ = np.zeros(1000.0)
    for s in neutrals:
        sumQ += Q[s]
    return sumQ

def T_new(T, sumQ, dz, lam_n, dt, RHO, Cp):
    
    # Defineing the change in thermal conduction in [W/(m*K)].
    dlam_n = np.zeros(999.0)
    for i in range(1, 998):
        dlam_n[i] = dlam_n[i + 1] - dlam_n[i - 1]
        dlam_n[0] = dlam_n[1]
        dlam_n[998] = dlam_n[997]
    
    # Setting up the coeficients and boundary conditions of the tri diagonal matrix.
    A = np.zeros(999.0) + 1.0 
    for i in range(999):
        A[i] += dlam_n[i]/(4.0*lam_n[i])
    A[998] = 1.0
    B = np.zeros(1000.0) - 2.0 - (RHO*Cp*np.power(dz, 2))/(lam_n*dt) ; B[0] = -1.0  ;  B[999] = -1.0
    C = np.zeros(999.0) + 1.0 
    for i in range(999):
        C[i] -= dlam_n[i]/(4.0*lam_n[i])
    C[0] = 0.0
    D = np.zeros(1000.0) - (np.power(dz,2)/lam_n)*(T*(RHO*Cp/dt) + sumQ) ; D[0] = -200.0 ; D[999] = 0.0
    
    # Building the matrix
    coef = np.zeros([1000.0, 1000.0])
    for i in range(999):
        coef[i+1,i] = A[i]
    for i in range(1000):
        coef[i,i] = B[i]
    for i in range(999):
        coef[i,i+1] = C[i]
    
    # Solving the matrix equation.
    T = np.linalg.solve(coef, D)
    #plt.plot(T,z*1E-3)
    return T

def ion_production_rate(Ps, n, I, data, ztop):
    # Creating a new number density of the proper key type so python doesn't shit itself.
    nn = {}
    nn['O+'] = n['O']
    nn['N+'] = n['N']
    nn['O2+'] = n['O2']
    nn['N2+'] = n['N2']
    for s in ions:
        Ps[s] *= 0
        for j in range(0, 37):
            Ps[s][0:ztop+1] += nn[s][0:ztop+1]*I[0:ztop+1,j]*data[s][j]
    return Ps
    
def calculate_ion_number_densities(ni, source, RM, dt):
    # Calculating the ion number densities as they vary in time.
    for s in ions:
            ni[s] = (ni[s] + source[s]*dt)/(1 + RM[s]*dt)
    return ni