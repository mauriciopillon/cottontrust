import requests
import random

# Inicie uma instância do ACA-Py ----------------------------------------------------------------------------------
#ACA_PY_URL = "http://localhost:8150"

# Defina as credenciais de autenticação da API --------------------------------------------------------------------
headers = {"X-API-Key": "secretkey"}

import requests

# Defina o número da porta inicial
initial_port = 8150

# Defina as credenciais de autenticação da API
headers = {"X-API-Key": "secretkey"}

# Crie uma lista de instâncias do ACA-Py
aca_py_instances = []


i = 0
while True:
    # Adicione o número da iteração ao número da porta inicial
    port = initial_port + i

    # Crie a URL base para a instância do ACA-Py
    url = f"http://localhost:{port}"

    # Tente obter o status da instância
    try:
        response = requests.get(f"{url}/status", headers=headers)
        response.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
        # Se a tentativa falhar, saia do loop
        break

    # Se a tentativa for bem-sucedida, adicione a instância à lista
    instance = {
        "url": url,
        "headers": headers
    }
    aca_py_instances.append(instance)

    # Crie um DID para a instância
    response = requests.post(f"{url}/wallet/did/create", headers=headers)
    response.raise_for_status()
    did = response.json()

    # Adicione o DID à instância
    print(f"Instância {i+1} criada com DID: {did}")
    instance['did'] = did

    i += 1

# Agora você tem uma lista de instâncias do ACA-Py que você pode manipular
# Por exemplo, aqui está como você pode obter o status de cada instância
for instance in aca_py_instances:
    response = requests.get(f"{instance['url']}/status", headers=instance['headers'])
    print(response.text)  # Imprime o status da instância
    
# Escolha duas instâncias aleatórias
instance1, instance2 = random.sample(aca_py_instances, 2)

# Crie uma nova conexão na instância 1
response = requests.post(
    f"{instance1['url']}/connections/create-invitation",
    headers=instance1['headers']
)
response.raise_for_status()
invitation = response.json()

# Verifique se os campos necessários estão presentes
assert 'invitation' in invitation
assert 'serviceEndpoint' in invitation['invitation']
assert 'recipientKeys' in invitation['invitation']

# Use a instância 2 para aceitar o convite da instância 1
response = requests.post(
    f"{instance2['url']}/connections/receive-invitation",
    headers=instance2['headers'],
    json=invitation['invitation']
)

# Verifique se a solicitação foi bem-sucedida
if response.status_code != 200:
    print(f"Erro ao receber convite: {response.status_code}, {response.text}")
else:
    response.raise_for_status()