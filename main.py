import requests
import random
import json

# Carregue os dados do arquivo JSON
with open('fardinhos_menor.json', 'r') as f:
    fardinhos = json.load(f)

#print(f"Carregados {fardinhos} fardinhos.")   

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
num_dids = 5  # Número de DIDs que você quer criar para cada instância

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
        "headers": headers,
        "dids": [],
        "atributos": {
            "id": fardinhos[i]["id"],
            "descricao_safra": fardinhos[i]["descricao_safra"],
            "etiqueta": fardinhos[i]["etiqueta"],
            "id_produto": fardinhos[i]["id_produto"],
            "descricao_algodao": fardinhos[i]["descricao_algodao"],
            "peso_bruto": fardinhos[i]["peso_bruto"],
            "peso_liquido": fardinhos[i]["peso_liquido"],
            "descricao_origem": fardinhos[i]["descricao_origem"]
        }
    }

    print(f"{instance['atributos']}\n")

    # Crie um número específico de DIDs para a instância
    for _ in range(num_dids):
        response = requests.post(f"{url}/wallet/did/create", headers=headers)
        response.raise_for_status()
        did = response.json()
        instance['dids'].append(did)
        print(f"=>Instância {i+1} criou DID {did}.")

    aca_py_instances.append(instance)

    print(f"Instância {i+1} criada com {num_dids} DIDs.")
    print("--------------------------------------------")
    i += 1

# Agora você tem uma lista de instâncias do ACA-Py que você pode manipular
# Por exemplo, aqui está como você pode obter o status de cada instância
for instance in aca_py_instances:
    response = requests.get(f"{instance['url']}/status", headers=instance['headers'])
    print(response.text)  # Imprime o status da instância
    print("--------------------------------------------")

# Escolha duas instâncias aleatórias
instance1, instance2 = random.sample(aca_py_instances, 2)

# Crie uma conexão entre as duas instâncias
response = requests.post(
    f"{instance1['url']}/connections/create-invitation",
    headers=instance1['headers'],
    json={"auto_accept": True},
)

invitation = response.json()
print(f"Convite de conexão criado pela instância 1: {invitation}")

response = requests.post(
    f"{instance2['url']}/connections/receive-invitation",
    headers=instance2['headers'],
    json=invitation,
)

print(f"Conexão criada entre instância 1 e instância 2: {response.text}")

