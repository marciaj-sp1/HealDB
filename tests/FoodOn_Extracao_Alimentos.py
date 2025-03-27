import requests
import pandas as pd
import re

# ===== 1. Carregar medicamentos do HEALDB =====
healdb = pd.read_csv("healdb_medicamentos.csv")

# Filtrar medicamentos que são anticoagulantes ou antitrombóticos
palavras_chave = r"(anticoagulante|fibrinolítico|antitrombótico|plaquetário)"
anticoagulantes = healdb[healdb['principio_ativo'].str.contains(palavras_chave, case=False, na=False)]

print("Medicamentos anticoagulantes identificados:")
print(anticoagulantes[['nome_medicamento', 'principio_ativo']])

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

# ===== 3. Correlacionar alimentos com os medicamentos =====
correlacao = []

for _, medicamento in anticoagulantes.iterrows():
    for _, alimento in alimentos.iterrows():
        correlacao.append({
            'Medicamento': medicamento['nome_medicamento'],
            'Princípio Ativo': medicamento['principio_ativo'],
            'Alimento': alimento['description'],
            'Interferência': 'Reduz a eficácia do anticoagulante, aumentando risco de trombose'
        })

# Criar DataFrame com a correlação
correlacao_df = pd.DataFrame(correlacao)
print("\nCorrelações identificadas:")
print(correlacao_df)

# ===== 4. Exportar resultado para CSV (opcional) =====
correlacao_df.to_csv("correlacao_alimentos_medicamentos.csv", index=False)
