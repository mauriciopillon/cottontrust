import asyncio
import json
import time
import csv
import random
import os

from aries_cloudagent.wallet.base import BaseWallet
from aries_cloudagent.wallet.indy import IndyWallet
from aries_cloudagent.wallet.error import WalletError
from aries_cloudagent.storage.basic import BasicStorage
from aries_cloudagent.protocols.didcomm.v2_0.models.diddoc import DIDDoc, PublicKey, PublicKeyType, Service

UBAs = []
Fardinhos = []
Clientes = []

tempos_transacao = []
tempo_criacao = []

cont_Uba = 0
cont_Far = 0
cont_Cli = 0

cont_Tran = 0

async def setup_identity(context, trustee, endorser):
    wallet: BaseWallet = await context.inject(BaseWallet, required=False)
    if not wallet:
        wallet = IndyWallet(context.settings)
        await wallet.open()
    did_info = await wallet.get_local_did(trustee['did'])
    did_doc = DIDDoc(did=did_info.did)
    controller = did_info.did
    ident = did_info.did
    verkey = did_info.verkey
    pk = PublicKey(
        did_info.did,
        "1",
        PublicKeyType.ED25519_SIG_2018,
        controller,
        verkey,
        True,
    )
    did_doc.set(pk)
    service = Service(
        did_info.did,
        "indy",
        "IndyAgent",
        ["didcomm"],
        "http://localhost:8000",
        [pk],
    )
    did_doc.set(service)
    await wallet.replace_local_did_metadata(did_info.did, {"endorser": endorser['did']})
      
async def create_wallet(context, trustee):
    wallet: BaseWallet = await context.inject(BaseWallet, required=False)
    if not wallet:
        wallet = IndyWallet(context.settings)
        await wallet.open()
    try:
        await wallet.create_local_did(seed=trustee['seed'])
    except WalletError:
        print(f"Wallet {trustee['name']} already exists")

async def create_and_store_my_did(context, trustee):
    wallet: BaseWallet = await context.inject(BaseWallet, required=False)
    if not wallet:
        wallet = IndyWallet(context.settings)
        await wallet.open()
    info = await wallet.create_local_did(seed=trustee['seed'])
    return info.did, info.verkey
    
async def create_cliente(context, cliente_data, trustee):
    # Criar uma nova carteira para o cliente
    cliente_wallet_config = json.dumps({'id': cliente_data['wallet_config']})
    cliente_wallet_credentials = json.dumps({'key': cliente_data['wallet_credentials']})
    await create_wallet(context, cliente_wallet_config, cliente_wallet_credentials)

    # Criar um novo DID para o cliente
    (cliente_did, cliente_key) = await create_and_store_my_did(context, {"seed": cliente_data['seed']})

    # Configurar a identidade do cliente
    await setup_identity(context, cliente_did, cliente_key, trustee['did'])

    # Emitir uma credencial para o cliente
    credential_manager = CredentialManager(context)
    offer = CredentialOffer(
        credential_preview=cliente_data['credential_data'],
        offer_request=cliente_data['offer_request']
    )
    exchange_record = V10CredentialExchange(
        credential_offer_dict=offer.serialize(),
        auto_issue=True
    )
    await credential_manager.create_offer(exchange_record) 

async def create_fardinho(context, fardinho_data, trustee):
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

async def create_uba(context, uba_data, trustee):
    # Criar uma nova carteira para a UBA
    uba_wallet_config = json.dumps({'id': uba_data['wallet_config']})
    uba_wallet_credentials = json.dumps({'key': uba_data['wallet_credentials']})
    await create_wallet(context, uba_wallet_config, uba_wallet_credentials)

    # Criar um novo DID para a UBA
    (uba_did, uba_key) = await create_and_store_my_did(context, {"seed": uba_data['seed']})

    # Configurar a identidade da UBA
    await setup_identity(context, uba_did, uba_key, trustee['did'])

    # Emitir uma credencial para a UBA
    credential_manager = CredentialManager(context)
    offer = CredentialOffer(
        credential_preview=uba_data['credential_data'],
        offer_request=uba_data['offer_request']
    )
    exchange_record = V10CredentialExchange(
        credential_offer_dict=offer.serialize(),
        auto_issue=True
    )
    await credential_manager.create_offer(exchange_record)
    
async def create_transaction(context, sender, receiver, custo_far, quant_far):
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
    credential_manager = CredentialManager(context)
    sender_offer = CredentialOffer(
        credential_preview={'balance': sender['balance'], 'quant_fardinho': sender['quant_fardinho']},
        offer_request=sender['offer_request']
    )
    sender_exchange_record = V10CredentialExchange(
        credential_offer_dict=sender_offer.serialize(),
        auto_issue=True
    )
    await credential_manager.create_offer(sender_exchange_record)

    # Emitir uma credencial para o destinatário
    receiver_offer = CredentialOffer(
        credential_preview={'balance': receiver['balance'], 'quant_fardinho': receiver['quant_fardinho']},
        offer_request=receiver['offer_request']
    )
    receiver_exchange_record = V10CredentialExchange(
        credential_offer_dict=receiver_offer.serialize(),
        auto_issue=True
    )
    await credential_manager.create_offer(receiver_exchange_record)

    end_time = time.time()
    duration = end_time - start_time
    print(f"\nA transacao levou {duration} segundos para ser concluida\n")
    tempos_transacao.append(duration)

    print(f"Transacao concluida: {sender['name']} enviou R${amount},00 para {receiver['name']} e recebeu {quant_far} Fardinhos")
    print(f"Saldo atual de {sender['name']}: R${sender['balance']},00 e {sender['quant_fardinho']} Fardinhos")
    print(f"Saldo atual de {receiver['name']}: R${receiver['balance']},00 e {receiver['quant_fardinho']} Fardinhos")
    print("--------------------------------------------")

async def run(context):
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
    await create_wallet(context, trustee)

    # Criar DIDs e configurar identidade
    (trustee['did'], trustee['key']) = await create_and_store_my_did(context, {"seed": trustee['seed']})
    await setup_identity(context, trustee, trustee)

    # Carregar dados de UBAs
    with open('ubas.json', 'r') as file:
        try:
            ubas_data = json.load(file)
        except json.JSONDecodeError:
            print("Arquivo UBA esta vazio.\n")
            ubas_data = []

    # Criar UBAs
    if ubas_data:
        for uba_data in ubas_data:
            time_uba = time.time()
            await create_uba(context, uba_data, trustee)
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
            await create_fardinho(context, fardinho_data)

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
            await create_cliente(context, cliente_data, trustee)
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

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
