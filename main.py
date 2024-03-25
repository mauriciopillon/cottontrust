import asyncio
import json
import time
import csv
import random
import os
import requests
import secrets
import aiohttp

from aries_cloudagent.wallet.askar import AskarWallet
from aries_cloudagent.wallet.models.wallet_record import WalletRecord
from aries_cloudagent.config.injection_context import InjectionContext
from aries_cloudagent.core.profile import Profile, ProfileManager
from aries_cloudagent.config.wallet import wallet_config
from aries_cloudagent.wallet.base import BaseWallet, KeyInfo
from aries_cloudagent.wallet.error import WalletError
from aries_cloudagent.protocols.issue_credential.v1_0.manager import CredentialManager
from aries_cloudagent.protocols.issue_credential.v1_0.messages.credential_offer import CredentialOffer
from aries_cloudagent.storage.askar import AskarStorage
from aries_cloudagent.protocols.issue_credential.v1_0.models.credential_exchange import V10CredentialExchange
from aries_cloudcontroller import AriesAgentController

UBAs = []
Fardinhos = []
Clientes = []

tempos_transacao = []
tempo_criacao = []

cont_Uba = 0
cont_Far = 0
cont_Cli = 0
cont_Tran = 0

def generate_seed():
    return secrets.token_hex(16)  # Gera uma string hexadecimal segura de 32 caracteres

def create_connection():
    #response = requests.post('http://localhost:8001/connections/create-invitation')
    response = requests.post('http://localhost:9000/connections/create-invitation')

    if response.status_code == 200:
        invitation = response.json()
        print("Convite criado com sucesso:", invitation)
    else:
        print("Erro ao criar convite:", response.status_code)

create_connection()

async def setup_identity(uba_did, uba_key, trustee_did):
    # Crie uma instância do controlador Aries
    controller = AriesAgentController(admin_url="http://localhost:9000")

    # Crie um novo DID
    response = await controller.wallet.create_did()

    # Verifique se a criação do DID foi bem-sucedida
    if "did" in response:
        print(f"DID criado com sucesso: {response['did']}")
        uba_did = response['did']
    else:
        print("Erro ao criar DID")

    # Atribua o DID criado ao agente
    response = await controller.wallet.assign_public_did(uba_did)

    # Verifique se a atribuição do DID foi bem-sucedida
    if "did" in response:
        print(f"DID atribuído com sucesso: {response['did']}")
    else:
        print("Erro ao atribuir DID")

    # Feche a conexão com o controlador Aries
    await controller.terminate()

async def create_and_store_my_did(trustee):
    response = requests.post('http://localhost:9000/wallet/did/create', data=json.dumps({'seed': trustee['seed']}))

    if response.status_code == 200:
        info = response.json()
        return info['result']['did'], info['result']['verkey']
    else:
        print("Erro ao criar DID:", response.status_code)
        return None, None  # Retorne None para ambos os valores se a requisição falhar
    
async def create_wallet(wallet_config, wallet_credentials):
    response = requests.post('http://localhost:9000/wallet/create', data=json.dumps({
        'wallet_config': wallet_config,
        'wallet_credentials': wallet_credentials
    }))

    if response.status_code != 200:
        print("Erro ao criar carteira:", response.status_code)

async def create_cliente(cliente_data, trustee):

    # Gerar uma nova seed
    cliente_data['seed'] = generate_seed()
    
    # Criar uma nova carteira para o cliente
    await create_wallet(cliente_data['wallet_config'], cliente_data['wallet_credentials'])

    # Criar um novo DID para o cliente
    (cliente_did, cliente_key) = await create_and_store_my_did(trustee)

    # Configurar a identidade do cliente
    await setup_identity(cliente_did, cliente_key, trustee['did'])

    # Emitir uma credencial para o cliente
    offer = {
        'credential_preview': cliente_data['credential_data'],
        'offer_request': cliente_data['offer_request']
    }
    response = requests.post('http://localhost:9000/issue-credential/send-offer', data=json.dumps(offer))

    if response.status_code != 200:
        print("Erro ao emitir credencial:", response.status_code) 


    # Criar uma nova carteira para o fardinho
    fardinho_wallet_config = json.dumps({'id': fardinho_data['wallet_config']})
    fardinho_wallet_credentials = json.dumps({'key': fardinho_data['wallet_credentials']})
    await create_wallet(fardinho_wallet_config, fardinho_wallet_credentials)

    # Criar um novo DID para o fardinho
    (fardinho_did, fardinho_key) = await create_and_store_my_did({"seed": fardinho_data['seed']})

    # Configurar a identidade do fardinho
    await setup_identity(fardinho_did, fardinho_key, trustee['did'])

    # Emitir uma credencial para o fardinho
    offer = {
        'credential_preview': fardinho_data['credential_data'],
        'offer_request': fardinho_data['offer_request']
    }
    response = requests.post('http://localhost:8001/issue-credential/send-offer', data=json.dumps(offer))

    if response.status_code != 200:
        print("Erro ao emitir credencial:", response.status_code)
    # Criar uma nova carteira para o fardinho
    fardinho_wallet_config = json.dumps({'id': fardinho_data['wallet_config']})
    fardinho_wallet_credentials = json.dumps({'key': fardinho_data['wallet_credentials']})
    await create_wallet(context, fardinho_wallet_config, fardinho_wallet_credentials)

    # Criar um novo DID para o fardinho
    (fardinho_did, fardinho_key) = await create_and_store_my_did(context, {"seed": fardinho_data['seed']})

    # Configurar a identidade do fardinho
    await setup_identity(context, fardinho_did, fardinho_key, trustee['did'])

    # Emitir uma credencial para o fardinho
    credential_manager = CredentialManager(context)
    offer = CredentialOffer(
        credential_preview=fardinho_data['credential_data'],
        offer_request=fardinho_data['offer_request']
    )
    exchange_record = V10CredentialExchange(
        credential_offer_dict=offer.serialize(),
        auto_issue=True
    )
    await credential_manager.create_offer(exchange_record)

async def create_fardinho(fardinho_data, trustee):
    # Gerar uma nova seed
    fardinho_data['seed'] = generate_seed()

    # Criar uma nova carteira para o fardinho
    fardinho_wallet_config = json.dumps({'id': fardinho_data['wallet_config']})
    fardinho_wallet_credentials = json.dumps({'key': fardinho_data['wallet_credentials']})
    await create_wallet(fardinho_wallet_config, fardinho_wallet_credentials)

    # Criar um novo DID para o fardinho
    (fardinho_did, fardinho_key) = await create_and_store_my_did({"seed": fardinho_data['seed']})

    # Configurar a identidade do fardinho
    await setup_identity(fardinho_did, fardinho_key, trustee['did'])

    # Emitir uma credencial para o fardinho
    offer = {
        'credential_preview': fardinho_data['credential_data'],
        'offer_request': fardinho_data['offer_request']
    }
    response = requests.post('http://localhost:8001/issue-credential/send-offer', data=json.dumps(offer))

    if response.status_code != 200:
        print("Erro ao emitir credencial:", response.status_code)

async def create_uba(uba_data, trustee):
    # Gerar uma nova seed
    uba_data['seed'] = generate_seed()

    # Criar uma nova carteira para a UBA
    uba_wallet_config = json.dumps({'id': uba_data['wallet_config']})
    uba_wallet_credentials = json.dumps({'key': uba_data['wallet_credentials']})
    await create_wallet(uba_wallet_config, uba_wallet_credentials)

    # Criar um novo DID para a UBA
    (uba_did, uba_key) = await create_and_store_my_did({"seed": uba_data['seed']})

    # Configurar a identidade da UBA
    await setup_identity(uba_did, uba_key, trustee['did'])

    # Emitir uma credencial para a UBA
    offer = {
        'credential_preview': uba_data['credential_data'],
        'offer_request': uba_data['offer_request']
    }
    response = requests.post('http://localhost:9000/issue-credential/send-offer', data=json.dumps(offer))

    if response.status_code != 200:
        print("Erro ao emitir credencial:", response.status_code)
    
async def create_transaction(sender, receiver, custo_far, quant_far):
    global cont_Tran
    cont_Tran += 1

    amount = custo_far * quant_far
    print("--------------------------------------------")
    print(f"Iniciando trasacao {cont_Tran}:")
    print(f"Saldo atual de {sender['name']}: R${sender['balance']},00")
    print(f"Saldo atual de {receiver['name']}: R${receiver['balance']},00")
    print(f"Quantidade de Fardinhos disponiveis em {receiver['name']}: {receiver['quant_fardinho']}")
    print(f"Quantidade de Fardinhos que {sender['name']} quer comprar: {quant_far}")
    print(f"Preco de cada Fardinho: R${custo_far},00")
    print(f"Valor total da transacao: R${amount},00")

    start_time = time.time()

    # Verifique se o remetente tem saldo suficiente
    if sender['balance'] < amount:
        print(f"{sender['name']} nao tem saldo suficiente para a transacao de compra dos fardinhos")
        return

    # Atualize o saldo do remetente
    sender['balance'] -= amount

    # Atualize a quantidade de Fardinhos do remetente
    sender['quant_fardinho'] += quant_far

    # Atualize o saldo do destinatário
    receiver['balance'] += amount

    # Atualize a quantidade de Fardinhos do destinatário
    receiver['quant_fardinho'] -= quant_far

    # Emitir uma credencial para o remetente
    sender_offer = {
        'credential_preview': {'balance': sender['balance'], 'quant_fardinho': sender['quant_fardinho']},
        'offer_request': sender['offer_request']
    }
    response = requests.post('http://localhost:9000/issue-credential/send-offer', data=json.dumps(sender_offer))

    if response.status_code != 200:
        print("Erro ao emitir credencial para o remetente:", response.status_code)

    # Emitir uma credencial para o destinatário
    receiver_offer = {
        'credential_preview': {'balance': receiver['balance'], 'quant_fardinho': receiver['quant_fardinho']},
        'offer_request': receiver['offer_request']
    }
    response = requests.post('http://localhost:9000/issue-credential/send-offer', data=json.dumps(receiver_offer))

    if response.status_code != 200:
        print("Erro ao emitir credencial para o destinatário:", response.status_code)

    end_time = time.time()
    duration = end_time - start_time
    print(f"\nA transacao levou {duration} segundos para ser concluida\n")
    tempos_transacao.append(duration)

    print(f"Transacao concluida: {sender['name']} enviou R${amount},00 para {receiver['name']} e recebeu {quant_far} Fardinhos")
    print(f"Saldo atual de {sender['name']}: R${sender['balance']},00 e {sender['quant_fardinho']} Fardinhos")
    print(f"Saldo atual de {receiver['name']}: R${receiver['balance']},00 e {receiver['quant_fardinho']} Fardinhos")
    print("--------------------------------------------")

async def run():
    # Carregar dados de teste
    with open('teste.json', 'r') as file:
        teste_data = json.load(file)

    # Configurar o agente trustee
    trustee = {
        'name': 'trustworthy_agent',
        'seed': '000000000000000000000000Trustee1',
        'wallet_config': json.dumps({'id': teste_data['wallet_config']}),
        'wallet_credentials': json.dumps({'key': teste_data['wallet_credentials']}),
        'role': 'TRUSTEE'
    }

    # Criar carteira para o trustee
    await create_wallet(trustee, trustee['wallet_credentials'])

    # Criar DIDs e configurar identidade
    (trustee['did'], trustee['key']) = await create_and_store_my_did({"seed": trustee['seed']})
    await setup_identity(trustee['did'], trustee['key'], trustee)

    # UBAS ----------------------------------------------------------------------------------------
    with open('ubas.json', 'r') as file:
        try:
            ubas_data = json.load(file)
        except json.JSONDecodeError:
            print("Arquivo UBA esta vazio.\n")
            ubas_data = []

    if ubas_data:
        for uba_data in ubas_data:
            time_uba = time.time()
            await create_uba(uba_data, trustee)
            endtime_uba = time.time()
            tempo_criacao.append(endtime_uba - time_uba)

        print("UBAs criados:\n")
        for item in UBAs:
            print(f"{item}\n")

    # FARDINHOS -----------------------------------------------------------------------------------

    with open('fardinhos.json', 'r') as file:
        try:
            fardinhos_data = json.load(file)
        except json.JSONDecodeError:
            print("Arquivo FARDINHOS esta vazio.\n")
            fardinhos_data = []

    if fardinhos_data:
        for fardinho_data in fardinhos_data:
            await create_fardinho(fardinho_data)

        print("Fardinhos criados:\n")
        for item in Fardinhos:
            print(f"{item}\n")

    # CLIENTES -----------------------------------------------------------------------------------

    with open('clientes.json', 'r') as file:
        try:
            clientes_data = json.load(file)
        except json.JSONDecodeError:
            print("Arquivo CLIENTES esta vazio.\n")
            clientes_data = []

    if clientes_data:
        for cliente_data in clientes_data:
            time_cli = time.time()
            await create_cliente(cliente_data, trustee)
            endtime_cli = time.time()
            tempo_criacao.append(endtime_cli - time_cli)

        print("Clientes do mercado externo criados:\n")
        for item in Clientes:
            print(f"{item}\n")

    # TRANSAÇÃO -----------------------------------------------------------------------------------------

    if UBAs and Clientes:
        num_transacoes = 4 # Quantidade de transações

        for _ in range(num_transacoes):
            sender= random.choice(Clientes)
            receiver = random.choice(UBAs)
            custo_far = receiver['preco_fardinho']
            quant_far = sender['quero_fardinho']
            
            await create_transaction(sender, receiver, custo_far, quant_far)

    response = requests.get('http://localhost:9000/status')
    print(response.json())

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
