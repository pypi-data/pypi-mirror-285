# SAMBA_ilum Copyright (C) 2024 - Closed source

import numpy as np
import subprocess
import shutil
import time
import sys
import os

#----------------
dir_codes = 'src'
dir_files = os.getcwd()
os.chdir(os.path.dirname(os.path.realpath(__file__)))
dir_samba = os.path.dirname(os.path.realpath(__file__))
print(f'{dir_samba}')
#--------------------

version = '1.0.0.28'

print(" ")
print("=============================================================")
print(f'SAMBA_ilum v{version} Copyright (C) 2024 ---------------------')
print("Closed source: Adalberto Fazzio's research group (Ilum|CNPEM)")
print("Author: Augusto de Lelis Araujo -----------------------------")
print("=============================================================")
print(" ")
print("   _____ ___    __  _______  ___       _ __              ")
print("  / ___//   |  /  |/  / __ )/   |     (_) /_  ______ ___ ")
print("""  \__ \/ /| | / /|_/ / __  / /| |    / / / / / / __ `___\ """)
print(" ___/ / ___ |/ /  / / /_/ / ___ |   / / / /_/ / / / / / /")
print("/____/_/  |_/_/  /_/_____/_/  |_|  /_/_/\__,_/_/ /_/ /_/ ")
print(f'                                                       v{version}')
print(" ")

#------------------------------------------------
# Checking for updates for SAMBA ----------------
#------------------------------------------------
try:
    url = f"https://pypi.org/pypi/{'samba_ilum'}/json"
    response = requests.get(url)
    dados = response.json()
    current_version = dados['info']['version']; current_version = str(current_version)
    if (current_version != version):
       print(" ")
       print("--------------------------------------------------------------")
       print("        !!!!! Your SAMBA version is out of date !!!!!         ")
       print("--------------------------------------------------------------")
       print("    To update, close the SAMBA and enter into the terminal:   ")
       print("                 pip install --upgrade samba                  ")
       print("--------------------------------------------------------------")
       print(" ")
       print(" ")
    ...
except Exception as e:
    print("--------------------------------------------------------------")
    print("    !!!! Unable to verify the current version of SAMBA !!!!   ")
    print("--------------------------------------------------------------") 
    print(" ")


print("######################################################################")
print("# O que deseja executar ? ============================================")
print("# ====================================================================")
print("# [0] Gerar inputs de execução do SAMBA                               ")
print("# --------------------------------------------------------------------")
print("# [1] Gerador de Heteroestruturas                                     ")
print("# [2] WorkFlow: High Throughput DFT (inputs + job)                    ")
print("# --------------------------------------------------------------------")
print("# [3] Personalizar inputs internos do WorkFlow (pasta INPUTS)         ")
print("######################################################################")
tarefa = input(" "); tarefa = int(tarefa)
print(" ")


if (tarefa == 0):
   shutil.copyfile(dir_codes + '/SAMBA_WorkFlow.input', dir_files + '/SAMBA_WorkFlow.input')
   shutil.copyfile(dir_codes + '/SAMBA_HeteroStructure.input', dir_files + '/SAMBA_HeteroStructure.input')


if (tarefa == 1):
   #--------------------------------------------------------------------------------------------------
   # Checking if the "SAMBA_HeteroStructure.input" file exists, if it does not exist it is created ---
   #--------------------------------------------------------------------------------------------------
   if os.path.isfile(dir_files + '/SAMBA_HeteroStructure.input'):
      0 == 0
   else:
      shutil.copyfile(dir_codes + '/SAMBA_HeteroStructure.input', dir_files + '/SAMBA_HeteroStructure.input')
   #---------------------------------------------------------------------------------------------------------

   print('')
   print('Atenção: ----------------------------------------------------------------------------')
   print('Verifique os parâmetros no arquivo SAMBA_HeteroStructure.input antes de prosseguir --')
   print('Estando tudo em ordem, aperte [ENTER] para prosseguir -------------------------------')
   print('-------------------------------------------------------------------------------------')
   confirmacao = input (" "); confirmacao = str(confirmacao)
   #------------------------------------------------------------
   exec(open(dir_files + '/SAMBA_HeteroStructure.input').read())
   exec(open(dir_codes + '/HeteroStructure_Generator.py').read())
   #-------------------------------------------------------------


if (tarefa == 2):
   #-------------------------------------------------------------------------------------------
   # Checking if the "SAMBA_WorkFlow.input" file exists, if it does not exist it is created ---
   #-------------------------------------------------------------------------------------------
   if os.path.isfile(dir_files + '/SAMBA_WorkFlow.input'):
      0 == 0
   else:
      shutil.copyfile(dir_codes + '/SAMBA_WorkFlow.input', dir_files + '/SAMBA_WorkFlow.input')
   #-------------------------------------------------------------------------------------------

   #----------------------------------------------------
   # Checking if the "WorkFlow_INPUTS" folder exists ---
   #----------------------------------------------------
   if os.path.isdir(dir_files + '/WorkFlow_INPUTS'):
      dir_inputs = dir_files + '/WorkFlow_INPUTS'
   else:
      dir_inputs = dir_codes + '/INPUTS'
   #------------------------------------------------------
   dir_inputs_vasprocar = dir_inputs + '/inputs_VASProcar'
   #------------------------------------------------------

   #------------------------------------------------
   # Checking if the "POTCAR" folder exists --------
   #------------------------------------------------
   if os.path.isdir(dir_files + '/POTCAR'):
      0 == 0
   else:
      print('')
      print('Atenção: -----------------------------------------')
      print('Pasta POTCAR e arquivos POTCAR_[ion] ausentes  ---')
      print('Insira e depois aperte [ENTER] para prosseguir ---')
      print('--------------------------------------------------')
      confirmacao = input (" "); confirmacao = str(confirmacao)
   #------------------------------------
   dir_pseudo = dir_files + '/POTCAR'
   shutil.copyfile(dir_codes + '/_info_pseudo.py', dir_pseudo + '/_info_pseudo.py')
   os.chdir(dir_pseudo)
   exec(open(dir_pseudo + '/_info_pseudo.py').read())
   os.chdir(dir_samba)
   #------------------

   print('')
   print('Atenção: ---------------------------------------------------------------------')
   print('Verifique os parâmetros no arquivo SAMBA_WorkFlow.input antes de prosseguir --')
   print('Estando tudo em ordem, aperte [ENTER] para prosseguir ------------------------')
   print('------------------------------------------------------------------------------')
   confirmacao = input (" "); confirmacao = str(confirmacao)
   #--------------------------------------------------------
   exec(open(dir_files + '/SAMBA_WorkFlow.input').read())
   #-----------------------------------------------------
   dir_o     = 'WorkFlow_output'
   dir_out   = dir_files + '/' + dir_o
   dir_virtual_python += '/bin/activate'
   #------------------------------------
   task = []
   for i in range(len(tasks)):
       if (tasks[i] == 'z-scan' or tasks[i] == 'xy-scan' or tasks[i] == 'relax'):  task.append(tasks[i])
       for j in range(len(type)):
           if (type[j] == 'sem_SO'):  rot = '' 
           if (type[j] == 'com_SO'):  rot = '.SO' 
           if (tasks[i] != 'z-scan' and tasks[i] != 'xy-scan' and tasks[i] != 'relax'):  task.append(tasks[i] + rot)
   #----------------------------------------------------------------------------------------------------------------
   exec(open(dir_codes + '/make_files.py').read())
   #----------------------------------------------


if (tarefa == 3):  shutil.copytree(dir_codes + '/INPUTS', dir_files + '/WorkFlow_INPUTS')


print(" ")
print("=============")
print("Concluido ===")
print("=============")
print(" ")
