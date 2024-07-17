# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 12:01:13 2023

@author: Franco, Bruno Agustín 
         
Copia de el modulo main.py pero con un iterador agregado para que haga la 
validación de multiples moleculas más sencillo. 
Basicamente permite ejecutar calculos de DP4+ en serie. 
Para que funcione la carpeta de .log debe estar bien rotulada con el ID del 
isomero seguido de un guiobajo. (ID_*_nmr.log)
El archivo de salida tendrá el nombre de la carpeta seleccionada, así que 
mejor mantenerlo sencillo. 
Los wtl pueden estar todos juntos en la misma carpeta. Nuevamente deben estar 
identificados con los isomeros a los que corresponde. Cuando pide seleccionar
los wtl se puede usar cualquier siempre y cuando esté en la misma carpeta en 
en donde están todos los demás . 
"""
import shutil, os, glob
import pandas as pd

from pathlib import Path

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
    mode, inputs = gui.gui_input()    
    
    if ('Custom' in mode and
        type (inputs) is str and
        'reparametrize' in inputs) :
        
        inputs = custom_gui.custom_input()
        
        if 'Input' in inputs['mode']: 
            output.gen_out_custom(inputs['mode'], 
                                  inputs['name'], 
                                  inputs['C_TMS'],
                                  inputs['H_TMS'],
                                  inputs['param'])
        elif 'Load' in inputs['mode']:             
            
            trap.check_NormalTermination()
            for molec in inputs['set']:
                trap.xlsx_trap(inputs, sheet= molec)
                
                
            standard, parameters, command = custom.parametrize(inputs['xlsx'], inputs['set'])
        
            output.gen_out_custom(command, 
                                  inputs['name'], 
                                  standard['C'],
                                  standard['H'],
                                  parameters)
    
    else: 
        #trap.xlsx_trap(inputs, sheet= 'shifts')
        trap.check_NormalTermination()
        
        if 'QM' in mode :
            data_base =  "data_base_QM.xlsx"
        elif 'MM' in mode:
            data_base =  "data_base_MM.xlsx"
        elif 'Custom' in mode:
            data_base =  "data_base_Custom.xlsx"
        
        data_base = (Path(__file__).parent / data_base).as_posix()
        
        stand = pd.read_excel(data_base,sheet_name='standard',index_col=0)
        stand = stand.loc[inputs['the_lev']]
        
        parameters = pd.read_excel(data_base,sheet_name=inputs['the_lev'],index_col=0)
        
        
        ### ACÁ SE MODIFICA CON UN ITERADOR PARA CADA XLSX --------------------
        def isomer_count(number):
            '''Determine the amount of isomeric candidates to be evaluated
            The files must be named by: isomerID_ * .log '''         
            files = []
            for file in glob.glob('*'): 
                if ('nmr' in file.casefold() and 
                    str(number).casefold() in file.casefold() and
                    any(extention in file[-4:] for extention in ['.out','.log'])): 
                    files.append(file)
            
            isomer_list =[]
            for file in files:
                if file.split('_',1)[0] not in isomer_list:
                    isomer_list.append(file.split('_',1)[0])
                else:
                    continue
            isomer_list.sort() ##RG
            isomer_list.sort(key=lambda s: len(s)) #RG    
            return isomer_list
        
        inputs ['warn'] = []
        
        
        di = os.path.split(inputs['xlsx'])[0]
        
        level = os.getcwd()
        level = os.path.split(level)[-1]
        
        files = glob.glob('*.xlsx', root_dir=di)
        files = [file for file in files if not '~$' in file]

        for file in files:             
            inputs['xlsx'] = file
            correct = os.path.split(file)[-1]
            correct = correct.split('_')[0]
            inputs['isom'] = isomer_count(correct[:-1])
            print( correct )
            
            outputs = dp4.calc( inputs['isom'], inputs['xlsx'], 
                               stand, parameters)
            
            mode = 'Rta-'+correct+f' {level}.xlsx'
            output.gen_out_dp4(mode, inputs, 
                               parameters, outputs, 
                               custom_mode = stand )
        
    gui.gui_end()   
    return
        

if __name__=='__main__': 

    main()
    
    

        
        
        
        
        
        
        
        
        
        