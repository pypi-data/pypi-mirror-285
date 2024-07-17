# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 16:56:19 2023

@author: Franco, Bruno Agustín 

Module capable of detecting inconsistencies in the inputs data.
The filters in this script avoid fatal error in the programme caused by 
the user incorrect usage.
"""

import numpy as np
import pandas as pd
import tkinter as tk
import os, glob, shutil

from collections import Counter
from sys import exit 

def error_found(sing):
    '''Generates a pop-up window indicating the type of error that is 
    preventing the program from running.
    You must indicate the sign you want to be displayed.
    '''
    warn_add = tk.Tk()
    warn_add.wm_title("DP4+ App")

    tk.Label(warn_add,text = '¡ Input Error !', 
             font = ("Arial Black", "12")).grid(row=1)
    tk.Label(warn_add,text = 'The following error has been found:',
             font = ("Arial Bold", "10")).grid(row=2, pady=(10,5))
    
    tk.Label(warn_add,text = sing ,
             font = ("Arial Bold", "10", "italic")).grid(row=3, pady=5)
    
    tk.Label(warn_add,text ='DP4+ App is about to close. Correct your input and try again.', 
             font = ("Arial Bold", "10")).grid(row=4, padx=10, pady=5)
    tk.Button(warn_add, text='Ok', 
              command=exit).grid(row=5, pady=(0,5), padx =10)
    
    warn_add.mainloop()
    return


def miss_column(data_df):
    '''Controls that the spreadsheets with the "wtl" contain the necessary 
    columns to operate
    '''    
    if not all(col in list(data_df.columns) for col in ['index','nuclei','sp2',
                                             'exp_data','exchange',
                                             'label 1', 'label 2', 'label 3']):
        print ('ACA1')
        error_found('Miss column in input spreadsheet')
    
    return    

def miss_data(data_df, isom, cant_isom ):
    '''Check that the information in the columns is correct and complete in 
    order to execute the calculations correctly.
    Each column has its specific requirements.
    '''
    #check exp_data
    for i, element in data_df['exp_data'].items():
        
        try: 
            element = float (element)
        except: 
            print ('ACA2')
            error_found('Not number value in "exp_data" column')
        
        if np.isnan(element) : 
            print ('ACA3')
            error_found('Miss value in "exp_data" column')
            return 
    
    #check nuclei
    for i, element in data_df['nuclei'].items():
        if element not in ['H','C']:
            print ('ACA4')
            error_found('Not C or H in "nuclei" column')
            return 
    
    #check diasterotopics 
    for diast, cant in Counter(data_df['exchange']).most_common():
        
        if type(diast) == float  : 
            continue
        
        elif cant != 2: 
            print (type(diast), diast)
            print ('ACA9')
            error_found('Uncoupled diasterotopic mark')
            return 
        
    #check sp2
    for mark in data_df['sp2'].unique():
        if mark == 1: continue
    
        if str(mark) not in ['nan','x','X','1']:
            error_found('sp2 wrongly identify. Use "x","X" or "1"')
            return 
    
    #check labels
    data_df = data_df.drop(['index','nuclei','sp2','exp_data','exchange'],axis=1)
    try : 
        temp = data_df
        temp [temp.isna()] = 0
        np.array(temp, dtype= int)
        del temp
    except: 
        print ('ACA5')
        error_found(f'Not interger number in column "label" in sheet {isom}')
        
    data_df = np.array(data_df, dtype= np.float64)
    if data_df.shape[1] % 3:
        print ('ACA6')
        error_found('Incorrect number of "label" columns. Should be multiple of 3')
        return 
    
    if data_df.shape[1]/3 > 1 and data_df.shape[1]/3 != cant_isom:
        print ('ACA7')
        error_found('Diferent amount of candidates and labels sets')
        return 
    
    loop = True
    while loop: 
        labels_set = data_df[:,:3]
        labels_set = np.nanmean(labels_set, axis = 1)
        
        if any(np.isnan(element) for element in np.nditer(labels_set)): 
            print ('ACA8')
            print (labels_set)
            error_found('Miss value in "label" column')
            return 
        
        if data_df.shape[1] == 3: 
            loop = False 
            continue 
        
        data_df = data_df [:,3:]
        
    return 
    
def xlsx_trap(file, sheet, cant_isom):
    '''Main function that executes the control of the spreadsheets used as 
    "wtl". Adapts the reading engine according to the file format.
    '''
    if 'xl' in file [-4:]: 
        eng = 'openpyxl'
    if 'od' in file [-4:]: 
        eng = 'odf'
    
    data = pd.read_excel(file, sheet_name=sheet , engine= eng)
    miss_column(data)
  
    miss_data(data , sheet, cant_isom)
        
    return
    
def exp_data_control(exp_df):
    '''Analyzes for the presence of suspiciously incorrect data.
    It may happen that the user has inadvertently specified some information 
    incorrectly
    '''
    highlights = []
    for cell, (index, row) in enumerate(exp_df.iterrows()):
        
        #cell+2 because in xlsx there is the header and the count starts in 0
        
        if (row['nuclei'] == 'H' and 
            row['exp_data'] > 6 and 
            np.isnan(row['sp2'])):
            highlights.append('C'+str(cell+2))
            
        elif (row['nuclei'] == 'C' and 
              row['exp_data'] > 120 and
              np.isnan(row['sp2'])):
            highlights.append('C'+str(cell+2))
    
        if row['nuclei'] == 'H' and row['exp_data'] > 14:
            highlights.append('B'+str(cell+2))
    
    return highlights

#-----------------------------------------------------------------------------

def sca_e_control(exp, e_matrix):
    '''Analyzes the results of the scaling errors coming from DP4+.
    Because the mathematical formula is applied blindly, this function is 
    appended to help identify gross errors.
    The experimental information and the error matrix must be indicated. As 
    a result, it returns a list of coded locations for printing in 
    spreadsheets with the output_module.py
    '''
    e_matrix = np.abs(e_matrix)
    C = (exp ['nuclei']=='C')
    H = exp['nuclei'].isin(['H','h'])
    
    C_hl = e_matrix > 10
    C_hl[H] = False
    C_hl = np.argwhere((C_hl == True))
    
    H_hl = e_matrix > 0.7
    H_hl[C] = False
    H_hl = np.argwhere((H_hl == True))

    hl = list (C_hl) + list (H_hl)
    highlights = []
    for cell in hl:
        
        col = chr(cell [1] + 6 + 64)
        row = cell [0] + 2
        highlights.append(col+str(row))            
    
    return highlights
    
    
def check_NormalTermination():
    '''Checks that the Gaussian calculations have finished correctly
    Those cases that "Normal Termination" is not found are removed to a 
    subfolder to continue with the calculation of DP4+.
    '''
    removed_files = False
        
    listing = []
    for file in glob.glob('*'): 
        if ('nmr' in file.casefold() and 
            any(extention in file[-4:] for extention in ['.out','.log'])): 
            listing.append(file)
    
    for file in listing:
        with open(file) as f:
            rline = f.readlines()
        if not " Normal termination" in rline[-1]:
            if not os.path.exists("Removed files"):
                os.makedirs("Removed files")
                
            shutil.move(file,'Removed files')         #mueve el .log en Error
            removed_files = True
            
    
    def end_all():
        warn_add.destroy()
        exit()
            
    if removed_files:
        
        warn_add = tk.Toplevel()
        warn_add.wm_title("DP4+ App")
    
        tk.Label(warn_add,text = '¡ Warning !', 
                 font = ("Arial Black", "12")).grid(row=1, column= 1,
                                                    columnspan=2)
        tk.Label(warn_add,text = 'Some Gaussian calcs do not terminate normally',
                 font = ("Arial Bold", "10")).grid(row=2,column= 1, 
                                                   columnspan=2, pady=10)
        tk.Label(warn_add,text = 'Files have been moved to "Removed files" inside the working folder',
                 font = ("Arial Bold", "10")).grid(row=3, column= 1,
                                                   columnspan=2)
        tk.Label(warn_add,text ='It is recommended to correct the inconsistency.', 
                 font = ("Arial Bold", "10")).grid(row=4, column= 1,
                                                   columnspan=2,
                                                   pady= (10,5), padx=10)
        tk.Button(warn_add, text='Continue anyway', 
                  command= warn_add.destroy).grid(row=5,column= 2,
                                                            pady=5)
        tk.Button(warn_add, text='Cancel proccess', 
                  command= end_all).grid(row=5,column= 1, pady=5)
        
        warn_add.wait_window()
            
                
                
                
                
                
                
                
                
                
                
                
                
                