import requests
import random
import json
import asyncio
import indy_vdr
import indy_vdr.bindings as bindings
import indy_vdr.ledger as ledger
import indy_vdr.request as vdr_req
import indy_vdr.pool as pl

# Configuração do pool
genesis_path = '/home/gabriel/cottontrust_ACA_Blockchain/genesis.txn'

# Carregue os dados do arquivo JSON
with open('fardinhos_menor.json', 'r') as f:
    fardinhos = json.load(f)

async def main():
  
    try:
        pool_ = await pl.open_pool(genesis_path)
        print('Pool aberto com sucesso!')
        print("--------------------------------------------")

        # Defina o número da porta inicial
        initial_port = 8150

        # Credenciais de autenticação da API
        headers = {"X-API-Key": "secretkey"}

        # Lista de instâncias do ACA-Py
        aca_py_instances = []

        i = 0

        num_dids = 1  # Número de DIDs para cada instância
        
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

            print(f"=>Instância {i+1}:{instance}\n")

            # Crie um número específico de DIDs para a instância
            for _ in range(num_dids):
                response = requests.post(f"{url}/wallet/did/create", headers=headers)
                response.raise_for_status()
                did = response.json()
                instance['dids'].append(did)
                print(f"=>Instância {i+1} criou DID {did}.\n")

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
        
        instance1, instance2 = random.sample(aca_py_instances, 2)
        print("Instâncias escolhidas aleatoriamente:\n")
        print(f"Instância A: {instance1}\n")
        print(f"Instância B: {instance2}")
        print("--------------------------------------------")

        did_teste1= instance1['dids'][0]['result']['did']
        did_nodo = 'Gw6pDLhcBcoQesN72qfotTgFa7cbuqZpkX3Xo6pLhPhv'
        try:      
            request = ledger.build_nym_request(did_teste1, did_nodo, None, None, None)
            print('o request eh: ',request)
            response = await instance1['pool'].submit_request(request)
            print('a resposta eh: ',response)
            print("--------------------------------------------") 
        except Exception as e:
            print(f"Ocorreu um erro ao enviar o DID para a blockchain: {e}")
            print("--------------------------------------------")        

        # Cria uma transação entre A e B ultilizando ACA-Py e o Indy VDR ( pool )
        # Construa a solicitação
        req = ledger.build_get_nym_request(
            submitter_did=instance1['dids'][0]['result']['did'],  # DID do remetente
            dest=instance2['dids'][0]['result']['did'],  # DID do destinatário
        )

        # Agora você pode enviar a solicitação para o pool
        resp = await instance1['pool'].submit_request(req)
        print(f"Resposta da solicitação: {resp}")

    except indy_vdr.error.VdrError as e:
        print(f'Erro ao abrir o pool: {e}')
        raise

# Chame a função main
asyncio.run(main())



