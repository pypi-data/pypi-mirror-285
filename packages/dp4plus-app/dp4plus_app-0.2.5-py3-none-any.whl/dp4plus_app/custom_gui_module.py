# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 12:09:02 2023

@author: Franco, Bruno Agustín 
               
Graphical interface module (GUI) to assist the data input to perform 
the reparameterization of dp4+
"""

import tkinter as tk
import pandas as pd
import os, glob, shutil

from random import randint
from tkinter import filedialog, messagebox
from pathlib import Path
from sys import exit


def custom_input ():
    ''' Main function of the application
    Contains the settings of the application widgets
    '''
    global custom_app
    custom_app = tk.Toplevel()
    custom_app.wm_title("Custom: New Level")
    custom_app.geometry("650x350") #(width x height)

    #-----------------------------------------------------------------
    label = tk.Label(custom_app, 
                     text='Reparametrization module')
    label.config(font = ("Arial Bold", "14"))
    label.grid(row=0,column=0,columnspan=2,sticky='W', padx=10)
    custom_app.columnconfigure(1, pad = 20)

    #----------------------------------------------------------------    
    #General widgets (wg)
    global mode_list, name_entry, button_final
    mode_list = tk.StringVar(custom_app)
    mode_list.set('Mode')
    mode_ddl = tk.OptionMenu(custom_app, mode_list,  
                             command = lambda x: mode_selection(),
                             *['Input parameters', 'Load files'])
    mode_ddl.configure(state='active', width = 17)
    mode_ddl.grid(row=1,column=0,sticky='W',pady = 5, padx=10)
    
    button_final = tk.Button(custom_app, text='Send',
                                font=("Arial Black", 10),
                                command= check_and_run )
     
    tk.Label(custom_app,text='Level Name :    ',
             anchor="e", width=20).grid(row=1,column=1,sticky='E')
    name_entry = tk.Entry(custom_app, width=40)
    name_entry.grid(row=1, column=2,columnspan=2, sticky="ew")
    
    #-----------------------------------------------------------------
    #"Input" widgets (wg)
    global param_frame, TMS_frame
    param_frame = tk.Frame(custom_app)
    TMS_frame = tk.Frame(custom_app)

    #-----------------------------------------------------------------
    #"Load" widgets (wg)
    global files_frame
    files_frame = tk.Frame(custom_app)
    
    custom_app.wait_window()
    
    if 'Input' in mode_list.get():
        return {'mode': mode,
                'name': name, 
                'C_TMS': C_TMS, 
                'H_TMS': H_TMS, 
                'param': table }
    
    elif 'Load' in mode_list.get():
        return {'mode': mode,
                'name': name, 
                'xlsx': custom_app.xlsx,
                'set': molecule_set}
    return

def mode_selection(): 
    ''' Change the widgets regarding the selection of the parameterization 
    mode. There are 2 modes: Input the data or Load files, so that it does 
    it automatically
    '''
    #clean the app if the user change the mode
    tk.Label(custom_app, 
             text=' ').grid(row=4,column=1,columnspan=2, sticky="nsew")
    for wg in [param_frame, TMS_frame, files_frame]:
        try: 
            wg.grid_forget()
        except: pass
    
    if 'Input' in mode_list.get():
        
        build_input_frames()
        TMS_frame.grid(row=2, column=0, columnspan=3, pady=10, sticky='S')
        param_frame.grid(row=3,column=0, sticky='N', columnspan=3)
        
    elif 'Load' in mode_list.get():
        
        button_download = tk.Button(files_frame, text=u'Download files \u21E9 ',
                               command = download)
        button_download.grid(row=0, column=0)
        
        button_dir = tk.Button(files_frame, text='Select Directory',
                               command = select_dir)
        button_dir.grid(row=1,column=0,sticky='W', pady=5)
        
        dir_label = tk.Label(files_frame, text='_', width=60, anchor='w')
        dir_label.grid(row=2,column=1,sticky='W', columnspan=2)
        
        button_xlsx = tk.Button(files_frame, text='Select Excel',
                               command= select_xlsx)
        button_xlsx.grid(row=3,column=0,sticky='W', pady=5)

        files_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", 
                         padx = 10, pady = 10)
    
    button_final.grid(row=4,column=0, pady=5, padx=10, sticky="w")
        
    return

def build_input_frames():
    ''' Build the grids for loading data in the "Input" mode.
    As its code is extensive, it was separated into an isolated function
    '''
    global C_entry, H_entry
    tk.Label(TMS_frame, text = 'TMS C: ').grid(row=0,column=0)
    C_entry = tk.Entry(TMS_frame)
    C_entry.grid(row=0,column=1)
    
    tk.Label(TMS_frame, text = 'TMS H: ').grid(row=0,column=2)
    H_entry = tk.Entry(TMS_frame)
    H_entry.grid(row=0,column=3)
    
    columns = [' ','ν','μ','σ']
    rows = ['Csp3','Csp2','Csca','Hsp3','Hsp2','Hsca']
    
    #set columns
    for i,col in enumerate(columns):
        nuclei_col = tk.Label(param_frame,text=col)
        nuclei_col.grid(row=0,column=i)
        
    #set rows/index
    for i,row in enumerate(rows):
        nuclei_col = tk.Label(param_frame,text=row)
        nuclei_col.grid(row=i+1,column=0)
        
    #set entrys
    global param_entrys
    param_entrys = pd.DataFrame(columns=columns[1:], 
                          index=rows)
     
    for i,row in enumerate(rows): 
        for j,col in enumerate(columns[1:]):
            if col == 'μ':
                if (row == 'Csca' or row == 'Hsca'):
                    tk.Label(param_frame, text='0.00').grid(row=i+1,column=j+1)
                    continue
            
            param_entrys.loc[row,col]=tk.Entry(param_frame)
            param_entrys.loc[row,col].grid(row=i+1,column=j+1)
            
    return

def download(): 
    '''Configuration and applications, from the download window to 
    parameterize with G09 calculations
    '''
    down_add = tk.Toplevel()
    down_add.wm_title("DP4+ App")
    
    tk.Label (down_add, text = 'Optimization Theory Level: ').grid(row=0,column=0,
                                                          pady=10, sticky='we',
                                                          columnspan=2)
    
    down_selec = tk.StringVar(down_add,'')
    for i,value in enumerate(['MMFF','B3LYP']):
        tk.Radiobutton(down_add, text= value, value=value,
                       variable= down_selec, indicator = 0, 
                       selectcolor = "light green", width = 10,
                       font = ('Arial','10')).grid(row=1,column=i,
                                                   pady= (0,10))
                                                        
    tk.Label (down_add, text = 'G09 command line: ').grid(row=2,column=0,
                                                          padx=5, sticky='we',
                                                          columnspan=2)
    aux_frame = tk.Frame(down_add)
    tk.Label(aux_frame, text = '# ').grid(row=0,column=0)
    command = tk.Entry(aux_frame, width = 40)
    command.grid(row=0,column=1)
    aux_frame.grid(row=3,column=0, padx=15, sticky='we',columnspan=2 )

    def change_commandline():
        '''Change the command line of .gjc files in the working folder.
        For this, they must be labeled with "# input"'''
        for file in glob.glob("*.gjc"):    
            with open(( file.rsplit( ".", 1 )[ 0 ] ) + ".gjc", "r+") as f:
                            content = f.read()
                            f.seek(0)
                            f.truncate()
                            f.write(content.replace('input', command.get()))
        return
    
    def copy_and_exit():
        '''Copy the folder of .gjc files to calculate their nmr and later be 
        used in automatic parameterization.
        Then, it changes its command line with a helper function and finally
        closes the program.
        '''
        desktop = os.path.normpath(os.path.expanduser("~/Desktop"))
        if down_selec.get() == '' :
            tk.Label(down_add,width=15,
                     text='Select optimization level').grid(row=5,column=0,
                                                            padx=5, sticky='we',
                                                            columnspan=2)
            return
        elif command.get() == '':
            tk.Label(down_add, width=15,
                     text='Insert the G09 command line').grid(row=5,column=0,
                                                              padx=5, sticky='we',
                                                              columnspan=2)
            return
        elif 'B3L' in down_selec.get():
            example_fold = (Path(__file__).parent / "nmr_custom"/'opt_B3LYP').as_posix()
        elif 'MMFF' in down_selec.get():
            example_fold = (Path(__file__).parent / "nmr_custom"/'opt_MMFF').as_posix()

        
        dst_folder = os.path.join(desktop,"nmr_custom")
        if  os.path.exists(dst_folder):
            dst_folder = dst_folder+f'_{str(randint(0, 100))}'
        
        shutil.copytree(example_fold, dst_folder)
        os.chdir(dst_folder)
        change_commandline()
        
        shutil.copy((Path(__file__).parent / "nmr_custom"/'custom_molecules_set.docx').as_posix(), 
                    dst_folder)
        shutil.copy((Path(__file__).parent / "nmr_custom"/'Data_traning_set.xlsx').as_posix(), 
                    dst_folder)
        
        messagebox.showinfo(title = 'DP4+App',
                            message=u' Folder Copy \u2713 \n"nmr_custom" has been created in your desktop\nThe program will restarts. Follow the user guide instructions to process the data')
        
        down_add.destroy()
        custom_app.destroy()
        return
        
    tk.Button(down_add, text=u'Download files \u21E9 ',
              command= copy_and_exit).grid(row=4, column = 0, pady = (5,10), columnspan=2)
    down_add.rowconfigure(5, minsize=30)

    down_add.wait_window()
    return

def select_xlsx():
    '''Select xlsx file with experimental data and asignation labels. 
    '''    
    custom_app.xlsx = filedialog.askopenfilename(title='Select Excel',
                                   filetypes=[('Excel files','*.xlsx'),
                                              ('All files','*')])
    xlsx_label = tk.Label(files_frame, width=60, anchor='w')
    xlsx_label.grid (row=3,column=1,sticky='W', columnspan=2)
    
    if custom_app.xlsx == '':
            xlsx_label['text'] = custom_app.xlsx = '<- Select exp. data file'
            return
    else:
        xlsx_label['text'] = custom_app.xlsx[:9]+'  . . .  '+custom_app.xlsx[-50:]

    return

def select_dir():
    '''Select directory folder with a pop up window 
    It changes the working directory to the path selected
    It checks to find the tms, .log, and "nmr" rotulated files 
    '''
    custom_app.direc = filedialog.askdirectory(title='Select directory')
    
    dir_label = tk.Label(files_frame, width=60, anchor='w')
    dir_label.grid(row=1,column=1,sticky='W', columnspan=2)
    
    molec_label = tk.Label(files_frame, text='_',
             width=60, anchor='w')
    molec_label.grid(row=2,column=1, columnspan=2, sticky="nsew")
    
    if not custom_app.direc:
        dir_label['text'] = custom_app.direc = '<- Select a folder '
        return
    
    os.chdir(custom_app.direc)
    
    files = []
    for file in glob.glob('*'): 
        if (any(extention in file[-4:] for extention in ['.out','.log'])): 
            files.append(file)
    
    if not files: 
        dir_label['text'] = custom_app.direc ='<- G09 files not found (.log or .out). Try again'
        return
    elif not any('nmr' in file.casefold() for file in files):
        dir_label['text'] = custom_app.direc ='<- "_nmr" G09 files not found. Try again'
        return
    elif not any('tms' in file.casefold() for file in files):
        dir_label['text'] = custom_app.direc ='<- TMS file not found. Try again'
        return

    
    dir_label['text'] = custom_app.direc[:9]+'  . . .  '+custom_app.direc[-50:]
    
    global molecule_set
    molecule_set, cant_comp = molecules_count() 
    molec_label['text'] = f'Parametrization set of {cant_comp} molecules'
    return    

def molecules_count():
    '''Determine the amount of molecules used for parametrization
    The files must be named by: name_ * _nmr.log 
    '''
    files = []
    for file in glob.glob('*'): 
        if ('nmr' in file.casefold() and 
            any(extention in file[-4:] for extention in ['.out','.log'])): 
            files.append(file)
    
    #takes out the TMS if its identify with "nmr" too
    for file in glob.glob('*'): 
        if ('nmr' in file.casefold() and 
            'tms' in file.casefold() and 
            any(extention in file[-4:] for extention in ['.out','.log'])): 
            files.remove(file)
    
    molecule_set =[]
    for file in files:
        if file.split('_',1)[0] not in molecule_set:
            molecule_set.append(file.split('_',1)[0])
        else:
            continue
    molecule_set.sort() ##RG
    molecule_set.sort(key=lambda s: len(s)) #RG    
    return molecule_set, len(molecule_set)

def check_and_run():
    '''Check that the data entered is correct to enable its sending to the 
    main module. 
    For each mode ("Input" or "Load") it controls different inputs.
    At the end it warns if the name introduce already exists and want to 
    update it
    '''
    #----------------------------------------------------------------    
    #check inputs 
    l_end = tk.Label(custom_app,text=' ',
                     width = 40, anchor='w')
    l_end.grid(row=4,column=1, columnspan= 2,sticky="nsew" )
    l_end['text'] = 'Checking data . . . '
    
    if len(name_entry.get()) < 5 :
        l_end['text'] = 'Invalid name. Too short'
        return
    
    if any(c in '!@#$%^&*()-+?_=,<>/" ' for c in name_entry.get()):
        l_end['text'] = 'Invalid name. Special character'
        return
    
    if any(c.isupper() for c in name_entry.get()):
        l_end['text'] = 'Invalid name. Uppercase'
        return
    
    if 'Input' in mode_list.get():
        
        if (C_entry.get() == '' or H_entry.get() == '') :
            l_end['text'] = 'Missing TMS'
            return
        try: 
            global C_TMS, H_TMS
            C_TMS = float( C_entry.get()) 
            H_TMS = float( H_entry.get())
        except: 
            l_end['text'] = 'Invalid TMS number'
            return
        
        
        global table
        table = param_entrys.copy()
        table.rename(columns={'μ':'m',
                              'ν':'n',
                              'σ':'s'}, inplace=True)
        
        for row in range(0,6): 
            for col in range(0,3):
                if type(param_entrys.iloc[row,col]) == float : 
                    table.iloc[row,col] = 0.0 
                    continue
                
                if param_entrys.iloc[row,col].get() == '' :
                    l_end['text'] = 'Missing parameter'
                    return 
                try:
                    table.iloc[row,col]=float(param_entrys.iloc[row,col].get())
                except:
                    l_end['text'] = 'Invalid parameter number'
                    return
                
                table.iloc[row,col]=param_entrys.iloc[row,col].get()

    #----------------------------------------------------------------    
    #check loads
    elif 'Load' in mode_list.get(): 
        try:     
            if ('<-' in custom_app.xlsx or 
                '<-' in custom_app.direc):
                l_end['text'] = 'Incorrect selection'
                return
            
            for molec in molecule_set: 
                if not molec in pd.ExcelFile(custom_app.xlsx).sheet_names:
                    l_end['text'] = f'{molec} sheet not found in xlsx file'
                    return
        except: 
            l_end['text'] = 'Missing selection'
            return
    
    #----------------------------------------------------------------        
    #internal function to terminate (has to go before its use in 'Ok' button)
    def save_level():
        '''Send the input data (global the variables and close the app) to
        the programme main module. 
        '''
        if name_entry.get() in levels: 
            warn_add.destroy()
            
        global mode, name 
        mode = mode_list.get()
        name = name_entry.get()

        #close widget    
        l_end['text'] = 'Processing . . .'
        button_final['state'] = 'disable'
    
        custom_app.after(1000, custom_app.destroy)

        return 
    #----------------------------------------------------------------     
    def change_name(): 
        warn_add.destroy()
        l_end['text'] = 'Choose other name'
        return
    
    
    #check name 
    data_base = (Path(__file__).parent / 'data_base_Custom.xlsx').as_posix()
    levels = pd.ExcelFile(data_base).sheet_names
    
    if name_entry.get() in levels: 
        warn_add = tk.Toplevel()
        warn_add.wm_title("DP4+ App")

        tk.Label(warn_add,text = '¡ Warning !', 
                 font = ("Arial Black", "12")).grid(row=1,column=1,
                                                   columnspan=2)
        tk.Label(warn_add,text =f'"{name_entry.get()}" already exists', 
                 font = ("Arial Bold", "10")).grid(row=2,column=1, 
                                                   pady=10, columnspan=2)
        tk.Label(warn_add,text ='Press "Ok" to update the level.', 
                 font = ("Arial Bold", "10")).grid(row=3,column=1, 
                                                   columnspan=2, padx=10)
        tk.Button(warn_add, text='Ok', 
                  command= save_level).grid(row=4,column= 2,
                                                            pady=5, padx =10)
        tk.Button(warn_add, text='Cancel', 
                  command=change_name).grid(row=4,column= 1, pady=5)
        
        warn_add.wait_window()
        return

    else: 
        save_level()
        return 

        

            
        