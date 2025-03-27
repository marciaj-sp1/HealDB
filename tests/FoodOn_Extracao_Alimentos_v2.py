# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 06:37:00 2024

@author: User
"""

import requests
import pandas as pd
import re

#
#Categorias identificadas como anticoagulantes dos medicamentos HealDB:
#ANTICOAGULANTES FIBRINOLITICOS E PROTEOLITICOS N/DIGE
#ANTITROMBOTICO
#ANTIAGREGANTE PLAQUETARIO
#ANTICOAGULANTES
#AGENTES ANTITROMBÓTICOS
#


# ===== 1. Carregar medicamentos do HEALDB =====
#healdb = pd.read_csv("healdb_medicamentos.csv")

# Filtrar medicamentos que são anticoagulantes ou antitrombóticos
palavras_chave = r"(anticoagulante|fibrinolítico|antitrombótico|plaquetário)"
#anticoagulantes = healdb[healdb['principio_ativo'].str.contains(palavras_chave, case=False, na=False)]

#print("Medicamentos anticoagulantes identificados:")
#print(anticoagulantes[['nome_medicamento', 'principio_ativo']])

# ===== 2. Consultar API USDA para alimentos ricos em vitamina K =====
url = "https://api.nal.usda.gov/fdc/v1/foods/search"
params = {
    "query": "vitamin K",
    "api_key": "68CoHatCcsCDGY9QWwTNn534UYN41uT5hdGAP9hY",  # Substituir pela sua API Key
    "pageSize": 10
}
response = requests.get(url, params=params)

if response.status_code == 200:
    alimentos = pd.DataFrame(response.json()['foods'])
    print("\nAlimentos ricos em vitamina K encontrados:")
    print(alimentos[['description']])
else:
    print(f"Erro na API: {response.status_code}")
