# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 11:46:25 2022

@author: Franco, Bruno A.

Auxiliar module by RCC Lab, to procces inputs files of NMR calc and correlate them to
in silico models and experimental data. It has 4 parts: 
        + get_exp_data: from the .xlsx and separate wtl of exp data
        + selections: generates a dictionary of Boolean elements that facilitates
                      matrix operations with specifics elements, like nuclei and error types
        + G09_tens_matix: generates "raw" tensors matrices. It ponderates conformational
                          landscape and keeps G09 order (so it manteins the labels)
        + sort_tens_matrix: correlates "raw" tensor matrix with in silico labels.
                            It also arrange diasterotopic nucleis based on exp data. 
"""
import pandas as pd
import numpy as np
import glob

from math import isnan 

##### AGREGAR RELATIVE IMPORTS
from . import bugs_a_warning_module as trap 

def get_exp_data(xlsx, sheet, isom_list=False):
    '''Reads "sheet" of .xlsx file given. 
    Determinates the exp data as a DataFrame and labels as NumpyArrays.
    If isom_list is given, because is used for dp4 calcs, it checks if there
    are different wtl for each candidate. 
    In case, there is only one set of labels the return of "wtl" would be a 
    np.array. 
    If there are several isomers with diferent sets of labels the return of
    "wtl" would be a dict() of np.array for each
    '''
    if 'xl' in xlsx[-4:]: 
        eng = 'openpyxl'
    if 'od' in xlsx[-4:]: 
        eng = 'odf'
    
    data = pd.read_excel(xlsx, sheet_name= sheet ,
                         engine= eng,)
    
    exp_data = data[['index','nuclei','sp2','exp_data','exchange']]
    for index, row in exp_data.iterrows(): 
        if any(x == row['sp2'] for x in ['x','X','1']):
            exp_data.loc[index,'sp2'] = 1
        
    data = data.drop(exp_data.columns,axis=1)
    
    if isom_list:
        
        if data.shape[1] > 3:
            wtl = dict ()
            for isom in isom_list: 
                wtl[isom] = np.array(data.iloc[:,:3])
                if data.shape[1] == 3: 
                    return exp_data, wtl
                data = data.iloc [:,3:]
                
    wtl = np.array(data)
    return exp_data, wtl

#%%
def selections(data):
    '''Classify types of nucleis (subsequently erros and probabilities types) 
    analizing the exp_data information. 
    Returns a pd.DataFrame with boolean columns (True or False) that indicates
    which nuclei of any correlated matrix corresponds to that gruoup'''
    selection = pd.DataFrame(columns=['C','C_sp2','C_sp3',
                                      'H','H_sp2','H_sp3'])
    selection ['C'] = data['nuclei'].isin(['C','c'])
    selection ['C_sp2'] = (data ['nuclei']=='C') & (data ['sp2']==1)
    selection ['C_sp3'] = (data ['nuclei']=='C') & (data ['sp2']!=1)
    
    selection ['H'] = data['nuclei'].isin(['H','h'])
    selection ['H_sp2'] = (data ['nuclei']=='H') & (data ['sp2']==1)
    selection ['H_sp3'] = (data ['nuclei']=='H') & (data ['sp2']!=1)
    
    return selection


#%%
def G09_tens_matrix(isomer_list, TMS = False):
    '''Using "get_scf_tensors() it builds the first tensor matrix of the 
    group of candidates (rows:nucleus, columns: isomers). It consider all 
    nucleus in the G09 order (there isn't any correlation process yet) 
    It uses an iterator to ponderate the confomers of each isomer in a 
    np.array().'''
    
    first_isom = True 
    
    for j, isom in enumerate(isomer_list):
        #generate matrix for each isomeric candidate (conf in columns)
        files = []
        for file in glob.glob('*'): 
            if ('nmr' in file.casefold() and 
                str(isom).casefold() == file.casefold().split('_')[0] and 
                any(extention in file[-4:] for extention in ['.out','.log'])): 
                files.append(file)
        
        if TMS: 
            files = []
            for file in glob.glob('*'): 
                if ('tms' in file.casefold() and 
                    any(extention in file[-4:] for extention in ['.out','.log'])): 
                    files.append(file)
        
        energies = list()
        conf_tens, energy = get_scf_tensors(files.pop(0), energies) #1st conf for template
        isom_matrix = np.empty((conf_tens.shape[0],len(files)+1))
        isom_matrix [:,0] = conf_tens
        energies.append(energy)
        
        #extract tens and energy from each conf
        for i, conf in enumerate (files):
            conf_tens, energy = get_scf_tensors(conf, energies)
            isom_matrix [:,i+1] = conf_tens
            energies.append(energy)
    
        #Boltzman Ponderation 
        energies = np.array(energies)*627.5095 #units change to kcal/mol 
        ground = energies.min()
        relativ_e= energies - ground             #relative energies
        P_Boltz=np.exp(-relativ_e*4.18/2.5)      #Boltzmann prob calc at 25°C
        contributions = P_Boltz / P_Boltz.sum()  #normalization   
        pond_isom = np.average(isom_matrix, weights=contributions, axis=1)
        
        if first_isom: 
            pond_matrix = np.empty((conf_tens.shape[0],len(isomer_list)))
            pond_matrix [:,0] = pond_isom
            first_isom = False
            continue
        
        pond_matrix [:,j] = pond_isom
        

    return pond_matrix

def get_scf_tensors(file, energies):
    '''Reads G09 calculus in the working folder. Sistematicaly stracts the 
    isotropic shielding tensors and SCF energies.
    Returns a np.array of tensors and energy as a float 
    It also corrects repeted energies (SHOULD CHECK THEY ARE NOT DUPLICATES)
    '''
    tensors=[]
    with open (file,'rt') as f:
        lines=f.readlines()
        for line in lines:
            if "SCF Done:" in line:
                energy=float(line.split()[4])
                
                if energy in energies:
                    energy += np.random.randint(10,100)/10**10
                
            if "Isotropic = " in line:
                tensors.append(float(line.split()[4]))
                
    return np.array(tensors), energy

#%%
def sort_tens_matrix(G09_tens_matrix, isomer_list, exp_data, wtl):
    '''Sort the raw tensor matrix order by the G09 labels following the 
    correlation labels informed by user. To sort and mean each isomer nucleis
    it uses the auxiliar funtion: sort_by_tens(G09_tens_list, isom_labels). 
    Returns a np.array() with tensor matrix correlated with the labels from
    input (rows: nucleus, columns: isom candidates)
    To finish, the diasterotopic nucleis are rearrange acoding to the exp_data'''
    sorted_tens_matrix= np.empty((exp_data.shape[0],len(isomer_list)))
    
    for i, isom in enumerate(isomer_list):
        if type(wtl) is dict:
            isom_tens = sort_isom_tens(G09_tens_matrix[:,i],
                                                     wtl[isom]) # <--
        else:
            isom_tens = sort_isom_tens(G09_tens_matrix[:,i],
                                                     wtl)       # <--
        sorted_tens_matrix[:,i] = diasterotopic(isom_tens, exp_data)
    
    return sorted_tens_matrix

def sort_isom_tens (G09_tens_list, isom_labels):
    '''Sort (correlate) the ponderated tensors of an isomer with the labels
    informed by user. It means equivalent nucleis if exists
    Requieres the tensor list order by G09 and the label matrix of the isom
    Returns a 1 dimensional np.array() (similar to a list but in np)'''
    
    isom_sorted_matrix= np.empty((isom_labels.shape[0],3))
    isom_sorted_matrix[:] = np.nan
    
    for y in range (isom_labels.shape[0]):
        for x in range (3):
            if not isnan(isom_labels[y,x]):
                try : 
                    index = int(isom_labels[y,x])
                    isom_sorted_matrix[y,x] = G09_tens_list[index-1] 
                    #-1 because G09 counts from 1 and Python from 0
                    
                except: 
                    trap.error_found(f'Correlation label {int(isom_labels[y,x])} is out of Gaussian matrix range')
                            
    return np.nanmean(isom_sorted_matrix, axis = 1)

def diasterotopic(tens_vector, exp_data):
    '''Rearranges the nuclei identified as diasterotopic, making the 
    largest experimental shift correspond to that calculated.
    For them, each pair of diasterotopic nuclei must be identified in the 
    exchange column with a letter.
    Returns a vector with the diasterotopics nucleis rearranged. 
    '''
    for diast in exp_data['exchange'].unique(): 
        #saltea los q no son diasterotopicos
        if (type(diast) == np.float64 or type(diast) == float) and isnan(diast): continue
        
        #se obtienen los indices de los nucleos diast
        nucleos = exp_data.loc[exp_data['exchange'] == diast].index.tolist()
        #for i,j in enumerate(nucleos):
        #    nucleos[i] = exp_data.index.get_loc(j)
            
        #se realiza un back up de los tensores 
        tensors = tens_vector[exp_data['exchange'] == diast]
        
        #los ordena de manera opuesta ya q el tensor es inversamente 
        #proporcional al desplazamiento
        max_d = max(exp_data.loc[exp_data['exchange'] == diast,'exp_data'])
        if exp_data.iloc[nucleos[0]]['exp_data'] == max_d:
             tens_vector[nucleos[0]] = min(tensors)
             tens_vector[nucleos[1]] = max(tensors)
        else:
            tens_vector[nucleos[0]] = max(tensors)
            tens_vector[nucleos[1]] = min(tensors)
            
    return tens_vector
