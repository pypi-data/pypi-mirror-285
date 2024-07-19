# SAMBA_ilum Copyright (C) 2024 - Closed source


import numpy as np
import shutil
import os


"""
INSERIR FUNÇÃO PARA VERIFICAR SE O ARQUIVO POSCAR INICIAL ESTA ESCRITO EM COORDENADAS DIRETAS OU CARTESIANAS
SE ESTIVER ESCRITO EM COORDENADAS CARTESIANAS, CONVERTER PARA COORDENADAS DIRETAS
TALVEZ CRIAR UMA FUNÇÃO COM ESTE PROPOSITO SEJA PRATICO PARA O CODIGO TODO 
"""


# Atenção: ================================================================
# O código foi escrito pensado em uma Heteroestrutura com n_Lattice = 2 ===
# Para redes com n_Lattice > 2 testes e generalizações devem ser feitas === 
#==========================================================================


deltaZ_i = replace_deltaZ_i         # Menor valor de separação
deltaZ_m = replace_deltaZ_m         # valor intermediário de separação
deltaZ_f = replace_deltaZ_f         # Maior valor de separação
passo_im = replace_passo_im         # Incremento no valor de deltaZ entre as etapas "i" e "m"
passo_mf = replace_passo_mf         # Incremento no valor de deltaZ entre as etapas "m" e "f"
vacuo    = replace_vacuo       # Vacuo mínimo aplicado aplicado a Heteroestrutura


"""
#----------------------------------------------------------------
# Testando a compatibilidade do arquivo POSCAR ------------------
#----------------------------------------------------------------
poscar = open('POSCAR', "r")
VTemp = poscar.readline().split()
poscar.close()
#-------------
crit = 0
for k in range(len(VTemp)):
    try:
       inteiro = int(VTemp[k])
       if (k > 0 and k < 3): crit += 1
    except ValueError:
       if (k == 0):  crit += 1
    #------------------------------
    if (len(VTemp) < 3 or crit < 3):
       print(f' ')
       print(f'========================================')
       print(f'Verifique o arquivo POSCAR utilizado!   ')
       print(f'INCOMPATIBILIDADE com o código detectada')
       print(f'========================================')
       print(f' ')
       #==========
       sys.exit()   
       #=========
"""



#----------------------------------------------------------------------------
# Função para listar todas as pastas dentro de um dado diretório ------------
#----------------------------------------------------------------------------
def list_folders(dir):
   l_folders = [name for name in os.listdir(dir) if os.path.isdir(os.path.join(dir, name))]
   return l_folders



#----------------
dir = os.getcwd()
#--------------------------
folders = list_folders(dir)
#---------------------------------------------------------
for i in range(len(folders)):  shutil.rmtree('folders[i]')
#--------------------------------------------------------------------
# if os.path.isfile('energy_scan.txt'):  os.remove('energy_scan.txt')



#==========================================================================
# Obtendo a altura no eixo-z dos diferentes materiais =====================
#==========================================================================
poscar = open('POSCAR', "r")
#--------------------------------
VTemp = poscar.readline().split()
n_Lattice = len(VTemp[1].replace('+', ' ').split())
nions_Lattice = []
for m in range(n_Lattice):  nions_Lattice.append(int(VTemp[m+2]))  
#----------------------------------------------------------------
VTemp = poscar.readline();  param = float(VTemp)
#---------------------------------------------------
for k in range(3): VTemp = poscar.readline().split()
fator_Z = float(VTemp[2])*param
#-------------------------------------------
for k in range(3): VTemp = poscar.readline()
#--------------------------------------------------------------
minZ = [0]*n_Lattice;  dZ = [0]*(n_Lattice +1);  dZ_total = 0.0
#--------------------------------------------------------------
for k in range(n_Lattice):
    vZ = []
    for m in range(nions_Lattice[k]):
        VTemp = poscar.readline().split()
        vZ.append(float(VTemp[2]))
    #-----------------------------
    dZ[k+1] = (max(vZ) - min(vZ))
    dZ_total += dZ[k+1]*fator_Z
    minZ[k] = min(vZ)
#----------------
poscar.close()
#-------------



#==========================================================================
# Deslocando os materiais para Z = 0.0 ====================================
#==========================================================================
poscar = open('POSCAR', "r")
poscar_new = open('POSCAR_temp', "w")
#------------------------------------
for k in range(8):
    VTemp = poscar.readline()
    poscar_new.write(f'{VTemp}')
for k in range(n_Lattice):
    for m in range(nions_Lattice[k]):
        VTemp = poscar.readline().split()
        temp_z = float(VTemp[2]) -minZ[k] +dZ[k]
        if (temp_z < 0.0):  temp_z = 0.0
        poscar_new.write(f'{float(VTemp[0])} {float(VTemp[1])} {temp_z} \n')
#-------------
poscar.close()
poscar_new.close()
#-----------------



#===========================================================
# Convertendo as coordenadas para a forma cartesiana =======
#===========================================================
poscar = open('POSCAR_temp', "r")
poscar_new = open('POSCAR_cart', "w")
VTemp = poscar.readline();  poscar_new.write(f'{VTemp}')
VTemp = poscar.readline();  poscar_new.write(f'{VTemp}')
VTemp = poscar.readline();  poscar_new.write(f'{VTemp}');  VTemp = VTemp.split();  A = [float(VTemp[0])*param, float(VTemp[1])*param, float(VTemp[2])*param]  
VTemp = poscar.readline();  poscar_new.write(f'{VTemp}');  VTemp = VTemp.split();  B = [float(VTemp[0])*param, float(VTemp[1])*param, float(VTemp[2])*param]
VTemp = poscar.readline();  poscar_new.write(f'{VTemp}');  VTemp = VTemp.split();  C = [float(VTemp[0])*param, float(VTemp[1])*param, float(VTemp[2])*param]
VTemp = poscar.readline();  poscar_new.write(f'{VTemp}')
VTemp = poscar.readline();  poscar_new.write(f'{VTemp}')
VTemp = poscar.readline();  poscar_new.write(f'Cartesian \n')
#-----------------------------------------------------------
# Escrita das coordenadas cartesianas ----------------------
#-----------------------------------------------------------
for k in range(n_Lattice):
    for m in range(nions_Lattice[k]):
        VTemp = poscar.readline().split()
        k1 = float(VTemp[0]); k2 = float(VTemp[1]); k3 = float(VTemp[2])
        coord_x = ((k1*A[0]) + (k2*B[0]) + (k3*C[0]))*param
        coord_y = ((k1*A[1]) + (k2*B[1]) + (k3*C[1]))*param
        coord_z = ((k1*A[2]) + (k2*B[2]) + (k3*C[2]))*param
        poscar_new.write(f'{coord_x:>28,.21f} {coord_y:>28,.21f} {coord_z:>28,.21f} \n')
#-------------
poscar.close()   
poscar_new.close()
#-----------------



#===========================================================
# Gerando os arquivos POSCAR para cada separação em Z ======
#===========================================================
z_scan0 = np.arange(deltaZ_i, deltaZ_m +passo_im, passo_im)
z_scan1 = np.arange(deltaZ_m +passo_mf, deltaZ_f +passo_mf, passo_mf)
z_scan = np.concatenate((z_scan0, z_scan1))
#------------------------------------------
for deltaZ in z_scan:
    deltaZ = round(deltaZ, 3)
    os.mkdir(str(deltaZ))
    shutil.copyfile('energy_scan.py', str(deltaZ) + '/energy_scan.py')
    shutil.copyfile('KPOINTS', str(deltaZ) + '/KPOINTS')
    shutil.copyfile('POTCAR', str(deltaZ) + '/POTCAR')
    shutil.copyfile('INCAR', str(deltaZ) + '/INCAR')
    #-----------------------------------------------
    poscar = open('POSCAR_cart', "r")
    poscar_new = open(str(deltaZ) + '/POSCAR', "w")
    VTemp = poscar.readline();  poscar_new.write(f'{VTemp}')
    VTemp = poscar.readline();  poscar_new.write(f'{VTemp}')
    VTemp = poscar.readline();  poscar_new.write(f'{VTemp}');  VTemp = VTemp.split();  A = [float(VTemp[0])*param, float(VTemp[1])*param, float(VTemp[2])*param]
    VTemp = poscar.readline();  poscar_new.write(f'{VTemp}');  VTemp = VTemp.split();  B = [float(VTemp[0])*param, float(VTemp[1])*param, float(VTemp[2])*param]
    VTemp = poscar.readline().split();  C = [float(VTemp[0])*param, float(VTemp[1])*param, float(VTemp[2])*param]
    #---------------------------------------------
    # temp_Z = (dZ_total + deltaZ_f + vacuo)/param
    temp_Z = (dZ_total + deltaZ + vacuo)/param
    poscar_new.write(f'{float(VTemp[0]):>28,.21f} {float(VTemp[1]):>28,.21f} {float(temp_Z):>28,.21f} \n')
    #-----------------------------------------------------------------------------------------------------
    VTemp = poscar.readline();  poscar_new.write(f'{VTemp}')
    VTemp = poscar.readline();  poscar_new.write(f'{VTemp}')
    VTemp = poscar.readline();  poscar_new.write(f'Cartesian \n')
    #------------------------------------------------------------
    for k in range(n_Lattice):
        for m in range(nions_Lattice[k]):
            VTemp = poscar.readline().split()
            coord_x = float(VTemp[0]); coord_y = float(VTemp[1]); coord_z = float(VTemp[2])
            #-------------------------------------------------------------------------------
            coord_z = coord_z + (vacuo/2)
            if (k > 0):  coord_z = coord_z + deltaZ
            poscar_new.write(f'{coord_x:>28,.21f} {coord_y:>28,.21f} {coord_z:>28,.21f} \n')
            #-------------------------------------------------------------------------------
    #-------------
    poscar.close()   
    poscar_new.close()
    #-----------------



# os.remove('POSCAR')
# os.remove('KPOINTS')
# os.remove('POTCAR')
# os.remove('INCAR')

os.remove('POSCAR_temp')
os.remove('POSCAR_cart')
