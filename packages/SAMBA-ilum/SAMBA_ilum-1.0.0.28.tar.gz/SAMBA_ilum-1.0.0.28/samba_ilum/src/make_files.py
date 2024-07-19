# SAMBA_ilum Copyright (C) 2024 - Closed source


#----------------------------------------------------------------------------
# Função para simular a digitação de comandos no terminal Linux -------------
#----------------------------------------------------------------------------
def command_terminal(command):
    command = command.split()
    vector_command = []
    for i in range(len(command)):  vector_command.append(command[i])
    subprocess.run(vector_command)

#----------------------------------------------------------------------------
# Função para listar todas os arquivos dentro de um dado diretório ----------
#----------------------------------------------------------------------------
def list_files(dir):
   l_files = [name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))]
   return l_files

#----------------------------------------------------------------------------
# Função para listar todas as pastas dentro de um dado diretório ------------
#----------------------------------------------------------------------------
def list_folders(dir):
   l_folders = [name for name in os.listdir(dir) if os.path.isdir(os.path.join(dir, name))]
   return l_folders

#----------------------------------------------------------------------------
# Resetando o diretório 'output' --------------------------------------------
#----------------------------------------------------------------------------
if os.path.isdir(dir_out):
   shutil.rmtree(dir_out)
   os.mkdir(dir_out)
else: os.mkdir(dir_out)
#----------------------


check_list = open(dir_out + '/check_list.txt', 'w')
check_list.close()


print(" ")
print("-------------------------------------------------------------------------")
print("Criando diretórios e copiando arquivos POSCAR e de input do VASProcar ---")
print("-------------------------------------------------------------------------")

files = list_files(dir_files + '/Structures')
#--------------------------------------------
t = 1.0; number = -1; n_passos = len(files)
#------------------------------------------

for i in range(len(files)):
    #----------------------
    number += 1
    porc = (number/n_passos)*100        
    #---------------------------
    if (porc >= t and porc <= 100):
       print(f'Progresso  {porc:>3,.0f}%')                 
       number += 1
       if (number == 1): t = 1
       if (number == 2): t = 1
       if (number >= 3): t = t + 1
       #--------------------------
              
    #---------------------------------
    os.mkdir(dir_out + '/' + files[i])
    #---------------------------------
    for j in range(len(task)):
        #==================================================
        dir_task = dir_out + '/' + files[i] + '/' + task[j]
        #==================================================
        os.mkdir(dir_task)
        shutil.copyfile(dir_files + '/Structures' + '/' + files[i], dir_task + '/POSCAR')
        #================================================================================
        if (task[j] == 'z-scan'):
           shutil.copyfile(dir_codes + '/z-scan_analysis.py', dir_task + '/z-scan_analysis.py')
           shutil.copyfile(dir_codes + '/energy_scan.py', dir_task + '/energy_scan.py')
           shutil.copyfile(dir_codes + '/z-scan.py', dir_task + '/z-scan.py')
           #---------------------------------------------------------------------------
           # Atualizando o arquivo z-scan.py ------------------------------------------
           #---------------------------------------------------------------------------
           with open(dir_task + '/z-scan.py', "r") as file:  content = file.read()
           content = content.replace('replace_deltaZ_i', str(deltaZ_i))
           content = content.replace('replace_deltaZ_m', str(deltaZ_m))
           content = content.replace('replace_deltaZ_f', str(deltaZ_f))
           content = content.replace('replace_passo_im', str(passo_im))
           content = content.replace('replace_passo_mf', str(passo_mf))
           content = content.replace('replace_vacuo', str(vacuo))
           with open(dir_task + '/z-scan.py', "w") as file: file.write(content)
        #=============================================
        if (task[j] == 'xy-scan'):
           shutil.copyfile(dir_codes + '/xy-scan_analysis.py', dir_task + '/xy-scan_analysis.py')
           shutil.copyfile(dir_codes + '/energy_scan.py', dir_task + '/energy_scan.py')
           shutil.copyfile(dir_codes + '/xy-scan.py', dir_task + '/xy-scan.py')
           #---------------------------------------------------------------------------
           # Atualizando o arquivo xy-scan.py -----------------------------------------
           #---------------------------------------------------------------------------
           with open(dir_task + '/xy-scan.py', "r") as file:  content = file.read()
           content = content.replace('replace_displacement_A1', str(displacement_A1))
           content = content.replace('replace_displacement_A2', str(displacement_A2))
           with open(dir_task + '/xy-scan.py', "w") as file: file.write(content)
        #=======================================================================
        if (task[j] == 'relax'):
           shutil.copyfile(dir_codes + '/contcar_update.py', dir_task + '/contcar_update.py')
           temp = dir_codes + '/contcar_update.py', dir_task
        #===================================================
        if (task[j][:3] == 'dos'):
           os.mkdir(dir_out + '/' + files[i] + '/' + task[j] + '/inputs') 
           shutil.copyfile(dir_inputs_vasprocar + '/input.vasprocar.dos', dir_task + '/inputs/input.vasprocar.dos')
        #==========================================================================================================
        if (task[j][:3] == 'scf'):
           os.mkdir(dir_out + '/' + files[i] + '/' + task[j] + '/inputs')
           shutil.copyfile(dir_inputs_vasprocar + '/input.vasprocar.locpot', dir_task + '/inputs/input.vasprocar.locpot')
        #================================================================================================================
        if (task[j][:5] == 'bands'):
           os.mkdir(dir_out + '/' + files[i] + '/' + task[j] + '/inputs')
           shutil.copyfile(dir_inputs_vasprocar + '/input.vasprocar.orbitals', dir_task + '/inputs/input.vasprocar.orbitals')
           shutil.copyfile(dir_inputs_vasprocar + '/input.vasprocar.locpot', dir_task + '/inputs/input.vasprocar.locpot') 
           shutil.copyfile(dir_inputs_vasprocar + '/input.vasprocar.bands', dir_task + '/inputs/input.vasprocar.bands')
           if (task[j][-3:] == '.SO'):
              shutil.copyfile(dir_inputs_vasprocar + '/input.vasprocar.spin', dir_task + '/inputs/input.vasprocar.spin') 
           #---------------------------------------
           poscar = open(dir_task + '/POSCAR', 'r')
           VTemp1 = poscar.readline().split();  poscar.close()
           #--------------------------------------------------           
           if (len(VTemp1) >= 3):
              #------------------
              shutil.copyfile(dir_inputs_vasprocar + '/input.vasprocar.location', dir_task + '/inputs/input.vasprocar.location')
              #-------------------------------------------------------------------------------------------------------
              label_materials = VTemp1[1].replace('+', ' ').split()
              range_ion_Lattice = []; nion = 0
              #------------------------------------
              for m in range(len(label_materials)):
                  range_ion_Lattice.append( str(1 + nion) + ':')
                  nion += int(VTemp1[m+2])
                  range_ion_Lattice[m] += str(nion) 
              #--------------------------------------------------------------------------------------------
              # Atualizando o arquivo input.vasprocar.location --------------------------------------------
              #--------------------------------------------------------------------------------------------
              with open(dir_task + '/inputs/input.vasprocar.location', "r") as file:  content = file.read()
              content = content.replace('replace_n_reg', str(len(label_materials)))
              for m in range(len(label_materials)):
                  content = content.replace('replace_label_Lattice' + str(m+1), str(label_materials[m].replace('_', '')))
                  content = content.replace('replace_nion_Lattice' + str(m+1), str(range_ion_Lattice[m]))
              with open(dir_task + '/inputs/input.vasprocar.location', "w") as file: file.write(content)
        #===============================================================================================
        if (task[j][:5] == 'bader'):
           #-----------------------------------------------------------------------------------
           shutil.copyfile(dir_codes + '/charge_transfer.py', dir_task + '/charge_transfer.py')
           shutil.copyfile(dir_codes + '/bader_update.py', dir_task + '/bader_update.py')
           dir_poscar = dir_out + '/' + files[i] + '/' + task[j]
           exec(open(dir_codes + '/bader_poscar.py').read())
           #------------------------------------------------



print(" ")
print("-------------------------------------------------------------------------")
print("Criando arquivos POTCAR para cada material ------------------------------")
print("-------------------------------------------------------------------------")

files0 = list_folders(dir_out)
#-------------------------------------------
t = 1.0; number = -1; n_passos = len(files0)
#-------------------------------------------

for i in range(len(files0)):
    #-----------------------
    number += 1
    porc = (number/n_passos)*100        
    #-----------------------------
    if (porc >= t and porc <= 100):
       print(f'Progresso  {porc:>3,.0f}%')                 
       number += 1
       if (number == 1): t = 1
       if (number == 2): t = 1
       if (number >= 3): t = t + 1
       #--------------------------

    for j in range(len(task)):
        #---------------------------
        if (task[j][:5] != 'bader'):
           dir_poscar = dir_out + '/' + files0[i] + '/' + task[j] + '/POSCAR'
           dir_potcar = dir_out + '/' + files0[i] + '/' + task[j] + '/POTCAR'
           exec(open(dir_codes + '/potcar.py').read())
           #------------------------------------------
        if (task[j][:5] == 'bader'):
           #---------------------------------------------------------------
           files1 = list_folders(dir_out + '/' + files0[i] + '/' + task[j])
           #---------------------------------------------------------------
           for k in range(len(files1)):
               if (files1[k] != 'Charge_transfer'):
                  dir_poscar = dir_out + '/' + files0[i] + '/' + task[j] + '/' + files1[k] + '/POSCAR'
                  dir_potcar = dir_out + '/' + files0[i] + '/' + task[j] + '/' + files1[k] + '/POTCAR'
                  exec(open(dir_codes + '/potcar.py').read())



print(" ")
print("-------------------------------------------------------------------------")
print("Criando arquivo KPOINT para cada material -------------------------------")
print("-------------------------------------------------------------------------")

#---------------------------------------------------
exec(open(dir_pseudo + '/cut_off_energy.py').read())
#---------------------------------------------------

files = list_folders(dir_out)
#------------------------------------------
t = 1.0; number = -1; n_passos = len(files)
#------------------------------------------

for i in range(len(files)):
    #---------------------------
    number += 1
    porc = (number/n_passos)*100        
    #---------------------------
    if (porc >= t and porc <= 100):
       print(f'Progresso  {porc:>3,.0f}%')                 
       number += 1
       if (number == 1): t = 1
       if (number == 2): t = 1
       if (number >= 3): t = t + 1
       #--------------------------

    for m in range(len(task)):
        #-----------------------------------------------------
        if (task[m][:7] == 'xy-scan'): k_dens = k_dens_xy_scan
        if (task[m][:6] == 'z-scan'):  k_dens = k_dens_z_scan
        if (task[m][:5] == 'relax'):   k_dens = k_dens_relax
        if (task[m][:5] == 'bader'):   k_dens = k_dens_bader
        if (task[m][:3] == 'scf'):     k_dens = k_dens_scf
        if (task[m][:3] == 'dos'):     k_dens = k_dens_dos
        #-------------------------------------------------
        if (task[m][:5] != 'bader'):
           #------------------------------------------------------
           path_vaspkit = dir_out + '/' + files[i] + '/' + task[m]
           exec(open(dir_codes + '/kpoints.py').read())
           #------------------------
        if (task[m][:5] == 'bader'):
           files1 = list_folders(dir_out + '/' + files0[i] + '/' + task[m])
           for k in range(len(files1)):
               if (files1[k] != 'Charge_transfer'):
                  #------------------------------------------------------------------------
                  path_vaspkit = dir_out + '/' + files[i] + '/' + task[m] + '/' + files1[k]
                  exec(open(dir_codes + '/kpoints.py').read())
                  #-------------------------------------------



print(" ")
print("-------------------------------------------------------------------------")
print("Criando arquivo INCAR para cada material --------------------------------")
print("-------------------------------------------------------------------------")

#------------------------------------------
t = 1.0; number = -1; n_passos = len(files)
#------------------------------------------

for i in range(len(files)):
    #----------------------
    number += 1
    porc = (number/n_passos)*100        
    #---------------------------
    if (porc >= t and porc <= 100):
       print(f'Progresso  {porc:>3,.0f}%')                 
       number += 1
       if (number == 1): t = 1
       if (number == 2): t = 1
       if (number >= 3): t = t + 1
       #--------------------------


    #-----------------------------------------------------------------------
    poscar = open(dir_out + '/' + files[i] + '/' + task[0] + '/POSCAR', 'r')
    VTemp = poscar.readline().split
    VTemp = poscar.readline();  param = float(VTemp)
    A1 = poscar.readline().split();  A1x = float(A1[0])*param;  A1y = float(A1[1])*param;  A1z = float(A1[2])*param;  A1 = np.array([A1x, A1y, A1z]);  mA1 = np.linalg.norm(A1)
    A2 = poscar.readline().split();  A2x = float(A2[0])*param;  A2y = float(A2[1])*param;  A2z = float(A2[2])*param;  A2 = np.array([A2x, A2y, A2z]);  mA2 = np.linalg.norm(A2)
    A3 = poscar.readline().split();  A3x = float(A3[0])*param;  A3y = float(A3[1])*param;  A3z = float(A3[2])*param;  A3 = np.array([A3x, A3y, A3z]);  mA3 = np.linalg.norm(A3)
    VTemp = poscar.readline()
    VTemp = poscar.readline().split()
    nion = 0
    for j in range(len(VTemp)):  nion += int(VTemp[j])
    poscar.close 
    #----------------------------------
    lreal = '.FALSE.';  amin = '# AMIN'
    if (nion > 30):  lreal = 'Auto'
    if ((mA1 > 50.0) or (mA2 > 50.0) or (mA3 > 50.0)):  amin = 'AMIN'
    #----------------------------------------------------------------


    #--------------
    ENCUT = -1000.0
    #-----------------------------------------------------------------------
    poscar = open(dir_out + '/' + files[i] + '/' + task[0] + '/POSCAR', 'r')
    #-----------------------------------------------------------------------
    for j in range(6):  VTemp1 = poscar.readline().split()
    poscar.close()
    #---------------------------
    for j in range(len(VTemp1)):
        temp = globals()['ENCUT_' + str(VTemp1[j])]   # Obtendo o valor da varíavel ENCUT para o correspondente átomo.
        if (ENCUT <= temp):  ENCUT = temp
    ENCUT = ENCUT*(1.3); ENCUT = float(int(ENCUT) +1)


    for j in range(len(task)):
        #---------------
        type_kpoints = 1
        #----------------------------------------------
        if (task[m][:5] == 'bands'):   type_kpoints = 0
        if (task[m][:7] == 'xy-scan'): k_dens = 1/k_dens_xy_scan
        if (task[m][:6] == 'z-scan'):  k_dens = 1/k_dens_z_scan
        if (task[m][:5] == 'relax'):   k_dens = 1/k_dens_relax
        if (task[m][:5] == 'bader'):   k_dens = 1/k_dens_bader
        if (task[m][:3] == 'scf'):     k_dens = 1/k_dens_scf
        if (task[m][:3] == 'dos'):     k_dens = 1/k_dens_dos
        #---------------------------------------------------


        if (task[j][:5] != 'bader'):
           #-------------------------------------------
           dir_incar = dir_inputs + '/INCAR_' + task[j]
           dir_output = dir_out + '/' + files[i] + '/' + task[j] + '/INCAR'
           #----------------------------------------------------------------
           shutil.copyfile(dir_incar, dir_output)
           #---------------------------------------------------------------
           # Atualizando o arquivo INCAR ----------------------------------
           #---------------------------------------------------------------
           with open(dir_output, "r") as file:  content = file.read()
           content = content.replace('replace_encut', str(ENCUT))
           content = content.replace('replace_lreal', str(lreal))
           content = content.replace('replace_vdW', str(vdW))
           content = content.replace('# AMIN', str(amin))
           if (type_kpoints == 1):
              if (type_k_dens == 3):
                 content = content.replace('# KSPACING', 'KSPACING = ' + str(k_dens))
                 content = content.replace('# KGAMMA',   'KGAMMA = ' + 'False')
              if (type_k_dens == 4):
                 content = content.replace('# KSPACING', 'KSPACING = ' + str(k_dens))
                 content = content.replace('# KGAMMA',   'KGAMMA = ' + 'True')
           with open(dir_output, "w") as file: file.write(content)


        if (task[j][:5] == 'bader'):
           #--------------------------------------------------------------
           files2 = list_folders(dir_out + '/' + files[i] + '/' + task[j])
           for k in range(len(files2)):
              if (files2[k] != 'Charge_transfer'):
                 #-------------------------------------------
                 dir_incar = dir_inputs + '/INCAR_' + task[j]
                 dir_output = dir_out + '/' + files[i] + '/' + task[j] + '/' + files2[k] + '/INCAR'
                 #-----------------------------------------------------------------------------------------------------------
                 shutil.copyfile(dir_codes + '/bader', dir_out + '/' + files[i] + '/' + task[j] + '/' + files2[k] + '/bader')
                 shutil.copyfile(dir_codes + '/chgsum.pl', dir_out + '/' + files[i] + '/' + task[j] + '/' + files2[k] + '/chgsum.pl')
                 shutil.copyfile(dir_incar, dir_output)
                 #------------------------------------------------------------
                 # Atualizando o arquivo INCAR -------------------------------
                 #------------------------------------------------------------
                 with open(dir_output, "r") as file:  content = file.read()
                 content = content.replace('replace_encut', str(ENCUT))
                 content = content.replace('replace_lreal', str(lreal))
                 content = content.replace('replace_vdW', str(vdW))
                 content = content.replace('# AMIN', str(amin))
                 if (type_kpoints == 1):
                    if (type_k_dens == 3):
                       content = content.replace('# KSPACING', 'KSPACING = ' + str(k_dens))
                       content = content.replace('# KGAMMA',   'KGAMMA = ' + 'False')
                    if (type_k_dens == 4):
                       content = content.replace('# KSPACING', 'KSPACING = ' + str(k_dens))
                       content = content.replace('# KGAMMA',   'KGAMMA = ' + 'True')
                 with open(dir_output, "w") as file: file.write(content)
           #--------------------------------------------------------------
           os.remove(dir_out + '/' + files[i] + '/' + task[j] + '/POSCAR')
           #--------------------------------------------------------------


for i in range(len(files)):
    #---------------------------------------------------------------------------------
    # Copiando códigos python para o diretorio principal -----------------------------
    #---------------------------------------------------------------------------------
    shutil.copyfile(dir_codes + '/lattice_plot3d.py', dir_out + '/' + files[i] + '/lattice_plot3d.py')
    shutil.copyfile(dir_codes + '/data-base_json.py', dir_out + '/' + files[i] + '/data-base_json.py')
    shutil.copyfile(dir_codes + '/output.py', dir_out + '/' + files[i] + '/output.py')
    #---------------------------------------------------------------------------------


###################################################################
# Escrevendo o arquivo de job para execução dos cálculos de DFT ###
###################################################################
exec(open(dir_codes + '/job.py').read())
#---------------------------------------
