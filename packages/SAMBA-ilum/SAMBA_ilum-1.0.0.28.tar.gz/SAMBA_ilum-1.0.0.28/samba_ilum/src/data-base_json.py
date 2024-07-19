# SAMBA_ilum Copyright (C) 2024 - Closed source


import json
import uuid
import sys
import os


# =========================================
# Verificando arquivos da sereme lidos: ===
# =========================================
l_file = 'null';  l_file_SO = 'null'
if os.path.isfile('output/info_scf.txt'):       l_file = 'info_scf.txt'
if os.path.isfile('output/info_bands.txt'):     l_file = 'info_bands.txt'
if os.path.isfile('output/info_scf_SO.txt'):    l_file_SO = 'info_scf_SO.txt'
if os.path.isfile('output/info_bands_SO.txt'):  l_file_SO = 'info_bands_SO.txt'
if (l_file == 'null' and l_file_SO == 'null'):  sys.exit(0)


name = 'teste'
id   = 'tese_1234'
unique_id = str(uuid.uuid4())


for n in range(2):
    #-------
    crit = 1
    #-----------
    if (n == 0):
       file = l_file;  db_name = 'info.json'
       if (file == 'null'):  crit = 0
    #-----------
    if (n == 1):
       file = l_file_SO;  db_name = 'info_SO.json'
       if (file == 'null'):  crit = 0

    print(crit)

    if (crit == 1):
       # ===================================================
       # Iniciando todas as tags com valores vazios "--" ===
       # ===================================================
       loop = 0;  name = '--';  id = '--';  unique_id = '--'
       nk = '--';  nb = '--';  ni = '--';  ne = '--'
       non_collinear = '--';  spin_orbit = '--';  lorbit = '--';  ispin = '--'
       vbm = '--';  cbm = '--';  gap = '--';  type_gap = '--';  ki_gap = '--';  kf_gap = '--'
       e_fermi = '--';  total_energy = '--';  param = '--';  fator_rec = '--'
       a1 = '--';  a2 = '--';  a3 = '--';  b1 = '--';  b2 = '--';  b3 = '--'
       vol_cell = '--';  vol_zb = '--';  k_points_direct = '--';  k_points_cart = '--';  k_path = '--'

       # ===========================================
       # Extraindo dados da saída do VASProcar =====
       # ===========================================
       with open('output/' + file, "r") as info: lines = info.readlines()
       #-----------------------------------------------------------------
       for i in range(len(lines)):
           VTemp = lines[i].replace('(', ' ( ').replace(')', ' ) ').replace(';', '').replace(',', '').split()
           if (len(VTemp) > 0):
              #----------------------------------------
              if (VTemp[0] == 'LNONCOLLINEAR'):  non_collinear = str(VTemp[2])
              #----------------------------------------
              elif (VTemp[0] == 'LSORBIT'):  spin_orbit = str(VTemp[2])
              #----------------------------------------
              elif (VTemp[0] == 'nº' or VTemp[0] == 'nÂº'):
                 if (VTemp[1] == 'k-points'):  nk = int(VTemp[3])
                 if (VTemp[5] == 'bands'):  nb = int(VTemp[7])
                 if (VTemp[1] == 'ions'):  ni = int(VTemp[3])
                 if (VTemp[5] == 'electrons'):  ne = float(VTemp[7])
              #----------------------------------------
              elif (VTemp[0] == 'LORBIT'):
                 lorbit = int(VTemp[2])
                 if (VTemp[3] == 'ISPIN'):  ispin = int(VTemp[5])
              #----------------------------------------
              elif (VTemp[0] == 'Last'):  vmb = int(VTemp[4])
              #----------------------------------------
              elif (VTemp[0] == 'First'):  cbm = int(VTemp[4])
              #----------------------------------------
              elif (VTemp[0] == 'GAP'):
                type_gap = str(VTemp[2])
                gap = float(VTemp[5])
                if (VTemp[8] == 'k-point'):
                   ki_gap = int(VTemp[9])
                   kf_gap = ki_gap
                if (VTemp[8] == 'k-points'):
                   ki_gap = int(VTemp[9])
                   kf_gap = int(VTemp[11])
              #----------------------------------------
              elif (VTemp[0] == 'Fermi'):  e_fermi = float(VTemp[3])           
              #----------------------------------------
              elif (VTemp[0] == 'free'):  total_energy = float(VTemp[4])   
              #----------------------------------------
              elif (VTemp[0] == 'Param.'):  param = float(VTemp[2])   
              #----------------------------------------
              elif (VTemp[0] == 'A1'):  a1 = [float(VTemp[4]), float(VTemp[5]), float(VTemp[6])]
              elif (VTemp[0] == 'A2'):  a2 = [float(VTemp[4]), float(VTemp[5]), float(VTemp[6])]
              elif (VTemp[0] == 'A3'):  a3 = [float(VTemp[4]), float(VTemp[5]), float(VTemp[6])]
              #----------------------------------------
              elif (VTemp[0] == 'Volume_cell'):  vol_cell = float(VTemp[2])   
              #----------------------------------------
              elif (VTemp[0] == '2pi/Param.'):  fator_rec = float(VTemp[2])   
              #----------------------------------------
              elif (VTemp[0] == 'B1'):  b1 = [float(VTemp[4]), float(VTemp[5]), float(VTemp[6])]
              elif (VTemp[0] == 'B2'):  b2 = [float(VTemp[4]), float(VTemp[5]), float(VTemp[6])]
              elif (VTemp[0] == 'B3'):  b3 = [float(VTemp[4]), float(VTemp[5]), float(VTemp[6])]
              #----------------------------------------
              elif (VTemp[0] == 'Volume_ZB'):  vol_zb = float(VTemp[2])   
              #----------------------------------------
              elif (VTemp[0] == 'k-points'):  loop = i+3


       if (file == 'info_bands.txt' or file == 'info_bands_SO.txt'):
          # =======================================================
          # Obtando e organizando as informações dos pontos-k =====
          # =======================================================
          info = open('output/' + file, "r")
          #---------------------------------
          if (loop != 0):
             #-----------------------------------------------------
             k_points_direct = []; k_points_cart = [];  k_path = []
             #---------------------------------------------
             for i in range(loop):  VTemp = info.readline()
             for i in range(nk):
                 VTemp = info.readline().split()
                 k_points_direct.append([float(VTemp[1]), float(VTemp[2]), float(VTemp[3])])
                 k_points_cart.append([float(VTemp[4]), float(VTemp[5]), float(VTemp[6])])
                 k_path.append(float(VTemp[7]))
          #-----------
          info.close()


       # ===========================================
       # Criando o Dicionário ======================
       # ===========================================
       dados = {
           "name": name,
           "id": id,
           "unique_id": unique_id,
           "nk": nk,
           "nb": nb,
           "ni": ni,
           "ne": ne,
           "non_collinear": non_collinear,
           "spin_orbit": spin_orbit,
           "lorbit": lorbit,
           "ispin": ispin,
           "vbm": vbm,
           "cbm": cbm,
           "gap": gap,
           "type_gap": type_gap,
           "ki_gap": ki_gap,
           "kf_gap": kf_gap,
           "e_fermi": e_fermi,
           "total_energy": total_energy,
           "param": param,
           "a1": a1,
           "a2": a2,
           "a3": a3,
           "vol_cell": vol_cell,
           "fator_rec": fator_rec,
           "b1": b1,
           "b2": b2,
           "b3": b3,
           "vol_zb": vol_zb,
           # "k_path": k_path,
           # "k_points_direct": k_points_direct,
           # "k_points_cart": k_points_cart
       }


       # ==================================================
       # Criando o arquivo .json ==========================
       # ==================================================
       with open('output/' + db_name, "w") as file_json:  json.dump(dados, file_json)


       """
       # ===============================================
       # Abrindo e lendo o data-base .json =============
       # ===============================================
       with open('output/' + db_name, "r") as file_json:
            date = json.load(file_json)
       #------------------------------------------------
       print("Dados do arquivo JSON:")
       for chave, valor in date.items():
           print(f"{chave}: {valor}")
       """
