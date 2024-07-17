# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 12:01:13 2023

@author: Franco, Bruno Agustín 
         RCC Lab Development
         

Main module of MM-DP4+ probability method.
    
"""
import shutil, os
import pandas as pd
import tkinter as tk

from PIL import ImageTk, Image  
from pathlib import Path
from tkinter import messagebox

##### AGREGAR RELATIVE IMPORTS 
from . import main_gui_module as gui
from . import bugs_a_warning_module as trap
from . import dp4_module as dp4
from . import custom_gui_module as custom_gui
from . import custom_module as custom 
from . import output_module as output


def create_exe():
    '''Creates a direc acces executable file in the user desktop'''
    desktop = os.path.normpath(os.path.expanduser("~/Desktop"))
    exe = shutil.which("dp4plus")
    
    shutil.copy(exe, desktop)
    return 

def main(): 
    '''AGREGAR DOCUMENTACION
    AGREGAR DOCUMENTACION
    AGREGAR DOCUMENTACION
    '''
    GUI = tk.Tk()
    GUI.attributes('-topmost',False)
    GUI.wm_title("DP4+App")
    title = tk.Label(GUI, text= 'Welcome to',
                     font = ("Times", "25", "bold"))
    title.pack()
    
    image1 = Image.open((Path(__file__).parent / 'logo_DP4app.png').as_posix())
    image1 = image1.resize((192, 237))
    test = ImageTk.PhotoImage(image1)
    label1 = tk.Label(image=test)
    label1.image = test
    label1.pack()
    
    #--------------------------------------------------------------------
    mode, inputs = gui.gui_input()        
    
    if not mode: # mode = None because it has to exit the program
        messagebox.showinfo(title = 'DP4+App',
                            message='Closing')   
        GUI.destroy()               
        return
        
    
    elif ('Custom' in mode and
        type (inputs) is str and
        'reparametrize' in inputs) :
        
        inputs = custom_gui.custom_input()
        
        if not mode: # mode = None because it has to exit the program
            messagebox.showinfo(title = 'DP4+App',
                                message=u'Closing \u2713 \nPress button to finish')   
            GUI.destroy()               
            return
        
        if 'Input' in inputs['mode']: 
            output.gen_out_custom(inputs['mode'], 
                                  inputs['name'], 
                                  inputs['C_TMS'],
                                  inputs['H_TMS'],
                                  inputs['param'])
        elif 'Load' in inputs['mode']:             
            
            trap.check_NormalTermination()
            for molec in inputs['set']:
                trap.xlsx_trap(inputs['xlsx'], sheet= molec,
                               cant_isom = 1)
                
                
            standard, parameters, command = custom.parametrize(inputs['xlsx'], inputs['set'])
        
            output.gen_out_custom(command, 
                                  inputs['name'], 
                                  standard['C'],
                                  standard['H'],
                                  parameters)
    
    else: 
        trap.xlsx_trap(inputs['xlsx'], sheet= 'shifts', 
                       cant_isom = len(inputs['isom']))
        trap.check_NormalTermination()
        
        if 'QM' in mode :
            data_base =  "data_base_QM.xlsx"
        elif 'MM' in mode:
            data_base =  "data_base_MM.xlsx"
        elif 'Custom' in mode:
            data_base =  "data_base_Custom.xlsx"
        
        data_base = (Path(__file__).parent / data_base).as_posix()
        
        if type(inputs['solvent']) == dict: 
            stand = inputs['solvent']
        
        else: 
            if 'Custom' in mode:
                inputs['solvent'] = 'standard'
            
            stand = pd.read_excel(data_base,
                                  sheet_name=inputs['solvent'],
                                  index_col=0)
            stand = stand.loc[inputs['the_lev']]
        
        parameters = pd.read_excel(data_base,sheet_name=inputs['the_lev'],index_col=0)
        
        outputs = dp4.calc( inputs['isom'], inputs['xlsx'], stand, parameters)
     
        output.gen_out_dp4( mode, inputs, 
                            parameters, outputs, stand )
        return
        
    GUI.destroy()       
        
    GUI.mainloop()
    
    return
        

if __name__=='__main__': 

    main()