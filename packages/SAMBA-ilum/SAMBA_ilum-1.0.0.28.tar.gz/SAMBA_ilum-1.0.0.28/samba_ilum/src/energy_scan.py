# SAMBA_ilum Copyright (C) 2024 - Closed source


import os

#===============================================
# Obtendo o caminho e o nome do diretório atual:
path_dir, name_dir = os.path.split(os.getcwd())
#===============================================

if os.path.isfile('../energy_scan.txt'):  energy = open('../energy_scan.txt', "a")
else:  energy = open('../energy_scan.txt', "w")

with open('OSZICAR') as file:
    lines = file.readlines()
VTemp = lines[-1].strip()

energia = VTemp.replace('=',' ').split()

energy.write(f'{name_dir} {energia[4]} \n')

energy.close()
