# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 13:23:46 2023

@author: Franco, Bruno Agustín 
         
DP4+ parameterization module
It uses the DP4+ nmr correlation and calculation modules, as well as having 
its own functions to complete the proccess. 
"""
from collections import Counter
from random import sample

import pandas as pd
import tkinter as tk
import numpy as np
import scipy.stats as st
import glob , os
#import os
#import matplotlib.pyplot as plt 

##### AGREGAR RELATIVE IMPORTS 
from . import correlation_module as nmr_correl
from . import dp4_module as dp4
from . import bugs_a_warning_module as warn
from . import output_module as output

def tms_mean(tms_g09_tens):
    '''Indicates the two most frequent tensors in a vector.
    It is designed for tms, where the most frequent tensor is the H nucleus 
    and the second is that of C
    '''
    nucleis = Counter(tms_g09_tens.T.tolist()[0])
    H = nucleis.most_common()[0][0]
    C = nucleis.most_common()[1][0]
    return {'C':C, 'H':H}

def add_errors(e_vectors, df_selections, uns_e, sca_e):
    '''Attaches the errors of a molecule to the global parameterization sets
    '''
    e_vectors['Csca'] = np.append(e_vectors['Csca'], sca_e[df_selections['C']])
    e_vectors['Hsca'] = np.append(e_vectors['Hsca'], sca_e[df_selections['H']])
    
    e_vectors['Csp2'] = np.append(e_vectors['Csp2'], uns_e[df_selections['C_sp2']])
    e_vectors['Csp3'] = np.append(e_vectors['Csp3'], uns_e[df_selections['C_sp3']])
    
    e_vectors['Hsp2'] = np.append(e_vectors['Hsp2'], uns_e[df_selections['H_sp2']])
    e_vectors['Hsp3'] = np.append(e_vectors['Hsp3'], uns_e[df_selections['H_sp3']])
    
    return e_vectors

def get_parameters(e_vectors):
    '''Estimates the parameters of the t studen probability distribution
    '''
    
    # out_file = os.path.normpath(os.path.expanduser("~/Desktop"))
    # out_file = os.path.join(out_file,'Tk_temp_Train.xlsx')
    # with pd.ExcelWriter(out_file) as writer:     
    #     for label,data in e_vectors.items(): 
    #         temp = pd.DataFrame(data)
    #         temp.to_excel(writer, sheet_name=label)
            
    param = pd.DataFrame(columns=['n', 'm', 's'],
                         index = ['Csp3','Csp2','Csca',
                                  'Hsp3','Hsp2','Hsca'])
    
    param.loc['Csca'] = st.t.fit(e_vectors['Csca'])
    param.loc['Hsca'] = st.t.fit(e_vectors['Hsca'])
    
    param.loc['Csp2'] = st.t.fit(e_vectors['Csp2'])
    print (len (e_vectors['Csp3']))
    print (st.t.fit(e_vectors['Csp3']))
    param.loc['Csp3'] = st.t.fit(e_vectors['Csp3'])
    
    param.loc['Hsp2'] = st.t.fit(e_vectors['Hsp2'])
    param.loc['Hsp3'] = st.t.fit(e_vectors['Hsp3']) 
    
    param.loc['Csca','m'] = 0.0
    param.loc['Hsca','m'] = 0.0
    
    return param

def get_command():
    '''saves the command line of 10% of the files used in the 
    parameterization
    '''    
    files = []
    for file in glob.glob('*'): 
        if ('nmr' in file.casefold() and 
            any(extention in file[-4:] for extention in ['.out','.log'])): 
            files.append(file)
    
    choose = sample(files, (len(files)//10)+1 )
    g09command =[]
    
    for file in choose: 
        with open(file,'r') as to_read: 
                for row in to_read.readlines(): 
                    if '#' in row:   
                        g09command.append(row)
                        break
                    
                    
    g09command = Counter(g09command).most_common()[0][0]
    return g09command

def n_warning (param): 
    '''Generates a popup window that allows you to change the degrees of 
    freedom obtained by other averages.
    This function is usually called when the sampling points are very few 
    giving a bad fit of the degrees of freedom of the t-Student
    '''
    warn_add = tk.Toplevel()
    warn_add.wm_title("DP4+ App")
    
    def change_df(): 
        param.loc['Csca','n'] = 7
        param.loc['Csp2','n'] = 8
        param.loc['Csp3','n'] = 10
        param.loc['Hsca','n'] = 4
        param.loc['Hsp2','n'] = 8
        param.loc['Hsp3','n'] = 4
        warn_add.destroy()
    
    tk.Label(warn_add,text = '¡ Warning !', 
             font = ("Arial Black", "12")).grid(row=1, column= 1,
                                                columnspan=2)
    tk.Label(warn_add,text = 'Very few sampling points has been provided',
             font = ("Arial Bold", "10")).grid(row=2,column= 1, 
                                               columnspan=2, pady=10)
    tk.Label(warn_add,text = 'They may be insufficient to correctly estimate the degrees of freedom',
             font = ("Arial Bold", "10")).grid(row=3, column= 1,
                                               columnspan=2)
    tk.Label(warn_add,text ='It is advisable to use averaged degrees of freedom.How do you want to proceed?', 
             font = ("Arial Bold", "10")).grid(row=4, column= 1,
                                               columnspan=2,
                                               pady= (10,5), padx=10)
    tk.Button(warn_add, text='Use REAL values', 
              command= warn_add.destroy).grid(row=5,column= 2,
                                                        pady=5)
    tk.Button(warn_add, text='Use AVERAGE values', 
              command= change_df).grid(row=5,column= 1, pady=5)
    
    warn_add.wait_window()
    
    return param 

def parametrize(xlsx: str, molec_set: list):
    '''Main algorithm of the parameterization process using G09 calculations.
    It uses the correlation module and some funtions of the dp4 module. 
    '''
    tms_tens = nmr_correl.G09_tens_matrix(['tms'], TMS=True ) 
    standard = tms_mean(tms_tens)
    
    e_vectors = {'Csca':np.empty(0), 'Csp2':np.empty(0), 'Csp3':np.empty(0),
                'Hsca':np.empty(0), 'Hsp2':np.empty(0), 'Hsp3':np.empty(0)}
     
    #esto es para que salga solo 1 vez el pop-up de highlights
    first_hl = True 
    
    #OCULTAR -----------------------------------
    #file = os.path.split(os.getcwd())[1]+' Train'
    #with pd.ExcelWriter(f'{file}.xlsx',engine="xlsxwriter") as writer:
    # ^^^^^^-----------------------------------
    
    for molec in molec_set:
        exp_data, wtl = nmr_correl.get_exp_data(xlsx, molec)
        df_selections = nmr_correl.selections(exp_data)
        
        tens = nmr_correl.G09_tens_matrix([molec]) #hay q dar una lista a la funcion
        tens = nmr_correl.sort_tens_matrix(tens, [molec], exp_data, wtl) 
        
        uns = dp4.get_uns_shifts(tens,df_selections, standard )
        sca = dp4.get_sca_shifts(uns, df_selections, exp_data)
        
        uns_e = dp4.calc_errors(uns,exp_data)
        sca_e = dp4.calc_errors(sca,exp_data)
        
        e_hl = warn.sca_e_control(exp_data, sca_e)
        exp_hl = warn.exp_data_control(exp_data)
        if e_hl + exp_hl: 
            output.add_highlights_warn(xlsx, molec, 
                                       e_hl, exp_hl, 
                                       pop_up = first_hl)
            first_hl = False
        
        e_vectors = add_errors(e_vectors, df_selections, uns_e, sca_e)
        
            
    #OCULTAR --------------------------------------------------------
            #matrix = np.concatenate( (tens,sca_e,sca,uns_e,uns), axis=1 )
            #matrix = pd.DataFrame(matrix,
            #                      columns=['tens','e_sca', 'd_sca', 'e_uns', 'd_uns'],
            #                      index=exp_data.index)
    
            #matrix = pd.concat([exp_data,matrix], axis=1)
            
            #matrix.to_excel(writer,
            #                sheet_name=str(molec), 
            #                index=True,
            #                float_format="%.4f")
            

        #matrix2 = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in e_vectors.items() ]))
        
        #matrix2.to_excel(writer,
        #                sheet_name= 'errors', 
        #                index=True,
        #                float_format="%.4f")
    ###^^^^^^----------------------------------------------------------
        
    parameters = get_parameters(e_vectors)
    if any (len(vector)<150 for e_type,vector in e_vectors.items()): 
        parameters = n_warning (parameters)
    
    
    #OCULTAR --------------------------------------------------------
    #fig, ax = plt.subplots(2,3)
    #i, j = 0 , 0
    #for label, param in parameters.iterrows(): 
    #    if j > 2: 
    #        j=0
    #        i+=1
    #    st.probplot( (e_vectors[label]-param['m'])/param['s'] , 
    #                dist = st.t(param['n']) , 
    #                plot = ax[i,j] )
    #    ax[i,j].set_title(label)
    #    j += 1
        
    #fig.tight_layout()
    #fig.savefig('t fitting check.png', dpi=300)
    ###^^^^^^----------------------------------------------------------
    
    command_line = get_command()
    
    return standard, parameters, command_line