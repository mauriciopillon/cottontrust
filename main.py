import requests

# Inicie uma instância do ACA-Py
ACA_PY_URL = "http://localhost:8151"

# Defina as credenciais de autenticação da API
headers = {"X-API-Key": "secretkey"}

# Defina o número de DIDs que você deseja criar
num_dids = 5

# Crie as DIDs
for _ in range(num_dids):
    response = requests.post(f"{ACA_PY_URL}/wallet/did/create", headers=headers)
    if response.status_code == 200:
        did_info = response.json()
        print(f"Novo DID: {did_info['result']['did']}, Verkey: {did_info['result']['verkey']}")
    else:
        print(f"Erro ao criar DID: {response.content}")

# Recupere e imprima todos os DIDs
response = requests.get(f"{ACA_PY_URL}/wallet/did", headers=headers)
if response.status_code == 200:
    dids = response.json()
    print("Todos os DIDs:")
    for did_info in dids['results']:
        print(f"DID: {did_info['did']}, Verkey: {did_info['verkey']}")
else:
    print(f"Erro ao recuperar DIDs: {response.content}")