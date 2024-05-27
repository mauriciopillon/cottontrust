import requests
import random
import json
import indy_vdr
import asyncio

# Configuração do pool
genesis_path = '/home/gabriel/cottontrust_ACA_Blockchain/genesis.txn'

async def main():
    global pool_

    try:
        pool_ = await indy_vdr.open_pool(genesis_path)
        print('Pool aberto com sucesso!')
        print("--------------------------------------------")
        
    except indy_vdr.error.VdrError as e:
        print(f'Erro ao abrir o pool: {e}')
        raise

# Chame a função main
asyncio.run(main())

# Agora você pode usar `pool` para enviar solicitações para a rede Indy
# Carregue os dados do arquivo JSON
with open('fardinhos_menor.json', 'r') as f:
    fardinhos = json.load(f)

# Defina o número da porta inicial
initial_port = 8150

# Credenciais de autenticação da API
headers = {"X-API-Key": "secretkey"}

# Lista de instâncias do ACA-Py
aca_py_instances = []
i = 0
num_dids = 5  # Número de DIDs para cada instância

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
        },
        "pool": pool_  # Adicione o pool à instância
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
# Obter o status de cada instância
for instance in aca_py_instances:
    response = requests.get(f"{instance['url']}/status", headers=instance['headers'])
    print(response.text)  # Imprima o status da instância
    print("--------------------------------------------")

