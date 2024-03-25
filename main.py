import requests
import json

# Inicie uma instância do ACA-Py
# Você precisará fazer isso em um terminal separado ou em um script de inicialização
# ACA_PY_URL é o endereço do seu ACA-Py (por exemplo, http://localhost:8150)

ACA_PY_URL = "http://localhost:8151"  # Atualizado para usar a porta 8151

# Crie um novo DID
# Crie um novo DID
headers = {"X-API-Key": "secretkey"}
response = requests.post(f"{ACA_PY_URL}/wallet/did/create", headers=headers)

# Verifique se a solicitação foi bem-sucedida
if response.status_code == 200:
    did_info = response.json()
    print(f"Novo DID: {did_info['result']['did']}")
else:
    print(f"Erro ao criar DID: {response.content}")