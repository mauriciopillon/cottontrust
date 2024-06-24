import asyncio
import json
import requests
import random

import base64
import nacl.signing
import nacl.encoding

import indy_vdr
from indy_vdr.ledger import build_nym_request, build_get_nym_request
from indy_vdr.pool import open_pool, Pool
from indy_vdr.error import VdrError

# Configuração do pool
genesis_path = '/home/gabriel/cottontrust_ACA_Blockchain/genesis.txn'

# Carregar dados do arquivo JSON
with open('fardinhos_menor.json', 'r') as f:
    fardinhos = json.load(f)

#def object_to_dict(obj):
    #return obj.__dict__
    
# Função para gerar par de chaves
def generate_keypair():
    signing_key = nacl.signing.SigningKey.generate()
    verify_key = signing_key.verify_key
    return {
        "private_key": signing_key.encode(encoder=nacl.encoding.HexEncoder).decode('utf-8'),
        "public_key": verify_key.encode(encoder=nacl.encoding.HexEncoder).decode('utf-8')
    }

# Função para assinar o pedido
def sign_request(request_json, signing_key):
    # Converte a chave de assinatura de hexadecimal para o objeto SigningKey
    signing_key = nacl.signing.SigningKey(signing_key, encoder=nacl.encoding.HexEncoder)
    # Serializa o JSON e converte para bytes
    request_bytes = json.dumps(request_json).encode('utf-8')
    # Assina a requisição
    signed_request = signing_key.sign(request_bytes)
    # Extrai a assinatura
    signature = signed_request.signature
    # Codifica a assinatura em base64
    signature_base64 = base64.b64encode(signature).decode('utf-8')
    
    # Verifique se este é o formato esperado pela blockchain
    # Exemplo: se a blockchain espera um campo 'signature' como string
    request_json['signature'] = signature_base64
    
    return request_json
# Função para criar DID
def create_did(url, headers, public_key):
    did_doc = {
        "method": "sov",
        "options": {
            "key_type": "ed25519",
            "verkey": public_key
        }
    }
    response = requests.post(f"{url}/wallet/did/create", headers=headers, json=did_doc)
    response.raise_for_status()
    return response.json()

# Function to send the NYM transaction
async def send_nym_transaction(pool_, submitter_did, target_did, verkey, signkey):
    try:
        nym_request = build_nym_request(submitter_did=submitter_did, dest=target_did, verkey=verkey)
        
        # Convert the request object to a dictionary
        nym_request_dict = json.loads(nym_request.body)
        
        # Sign the request
        signed_request = sign_request(nym_request_dict, signkey)
        
        # Send the request and get the response
        response = await pool_.submit_request(signed_request)
        print(f"Resposta da transação NYM: {response}")
        print("--------------------------------------------")
    except Exception as e:
        print(f"Erro ao enviar transação NYM: {e}")
        print("--------------------------------------------")

# Main async function
async def main():
    try:
        pool_ = await open_pool(transactions_path=genesis_path)
        print('Pool aberto com sucesso!')
        print("--------------------------------------------")

        initial_port = 8150
        headers = {"X-API-Key": "secretkey"}
        aca_py_instances = []

        i = 0
        num_dids = 1
        
        while True:
            port = initial_port + i
            url = f"http://localhost:{port}"

            try:
                response = requests.get(f"{url}/status", headers=headers)
                response.raise_for_status()
            except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
                break

            instance = {
                "url": url,
                "headers": headers,
                "dids": [],
                "private_keys": [],
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
                "pool": pool_
            }

            print(f"=>Instância {i+1}:{instance}\n")

            for _ in range(num_dids):
                keypair = generate_keypair()
                did = create_did(url, headers, keypair['public_key'])
                instance['dids'].append(did)
                instance['private_keys'].append(keypair['private_key'])
                print(f"=>Instância {i+1} criou DID {did} com chave privada {keypair['private_key']}.\n")

            aca_py_instances.append(instance)

            print(f"Instância {i+1} criada com {num_dids} DIDs.")
            print("--------------------------------------------")
            i += 1

        for instance in aca_py_instances:
            response = requests.get(f"{instance['url']}/status", headers=instance['headers'])
            print(response.text)
            print("--------------------------------------------")
        
        instance1, instance2 = random.sample(aca_py_instances, 2)
        print("Instâncias escolhidas aleatoriamente:\n")
        print(f"Instância A: {instance1}\n")
        print(f"Instância B: {instance2}")
        print("--------------------------------------------")

        did_teste1 = instance1['dids'][0]['result']['did']
        did_teste1_verkey = instance1['dids'][0]['result']['verkey']
        did_teste1_signkey = instance1['private_keys'][0]

        did_teste2 = instance2['dids'][0]['result']['did']
        did_teste2_verkey = instance2['dids'][0]['result']['verkey']
        did_teste2_signkey = instance2['private_keys'][0]

        try:      
            await send_nym_transaction(pool_, did_teste1, did_teste1, did_teste1_verkey, did_teste1_signkey)
            await send_nym_transaction(pool_, did_teste2, did_teste2, did_teste2_verkey, did_teste2_signkey)

        except Exception as e:
            print(f"Ocorreu um erro ao enviar o DID para a blockchain: {e}")
            print("--------------------------------------------")        

        req = build_get_nym_request(
            submitter_did=instance1['dids'][0]['result']['did'],
            dest=instance2['dids'][0]['result']['did'],
        )

        resp = await pool_.submit_request(req)
        print(f"Resposta da solicitação: {resp}")

        pool_.close()

    except VdrError as e:
        print(f'Erro ao abrir o pool: {e}')
        raise

asyncio.run(main())
