import asyncio
import json
import time
import csv
import random
import os

from indy import ledger, pool, error

import hashlib

from indy_vdr import pool, ledger
from aries_askar import wallet
from anoncreds import did
from indy_cli_rs import ErrorCode, IndyError

from didkit import DIDKit
from aries_askar import AskarStore

UBAs = []
Fardinhos = []
Clientes = []


tempos_transacao = []
tempo_criacao = []


cont_Uba = 0
cont_Far = 0
cont_Cli = 0

cont_Tran = 0

async def setup_identity(identity, trustee):
    print('cheguei no setup identity')
    did_safe = 'V4SGRU86Z58d6TV7PBUe6f'
    verkey_safe = '~CoRER63DVYnWZtK8uAzNbx'
    
    # Create a new DID using DIDKit
    did_result = DIDKit.generate_ed25519_key()
    identity['did'] = did_result['did']
    identity['key'] = did_result['key']

    # Store the DID and key using Askar
    store = AskarStore()
    await store.open()
    await store.insert(identity['did'], identity['key'])
    await store.close()
      
async def create_wallet(Entidade):
    print("\"{}\" -> Criando Carteira(wallet)".format(Entidade['name']))

    try:
        # Create a new Askar profile (equivalent to a wallet in indy)
        profile = await AskarProfile.create(Entidade['wallet_config'], Entidade['wallet_credentials'])
        Entidade['wallet'] = profile
    except Exception as e:
        print("\"{}\" -> Falha ao criar carteira".format(Entidade['name']))
        print(e)
        raise e
    
def create_seed(contador, nome):
    # Create a hash of the name and counter
    seed = hashlib.sha256((str(nome) + str(contador)).encode()).hexdigest()
    # Return the first 32 characters of the hash
    return seed[:32]

async def create_cliente(pool_, cliente_data, trustee):
    global cont_Cli
    cont_Cli += 1

    print(f"\nCriando Clientes {cont_Cli} - Cadastre")

    CLIENTE = {
        'name': cliente_data['name'],
        'Endereco - Rua': cliente_data['Endereco - Rua'],
        'Endereco - Bairro': cliente_data['Endereco - Bairro'],
        'Endereco - Cidade': cliente_data['Endereco - Cidade'],
        'Endereco - Estado': cliente_data['Endereco - Estado'],
    }

    # Create a new DID for the client
    did_result = DIDKit.generate_ed25519_key()
    CLIENTE['did'] = did_result['did']
    CLIENTE['key'] = did_result['key']

    # Store the DID and key using Askar
    store = AskarStore()
    await store.open()
    await store.insert(CLIENTE['did'], CLIENTE['key'])
    await store.close()

    # Add the client to the pool
    pool_.append(CLIENTE)  
    

async def create_fardinho(pool_, fardinho_data):
    global cont_Far
    cont_Far += 1

    print(f"Criando Fardinho {cont_Far} - Cadastre")

    FARDINHO = {
        'name': fardinho_data['name'],
        # Add any other data from fardinho_data as needed
    }

    # Create a new DID for the fardinho
    did_result = DIDKit.generate25519_key()
    FARDINHO['did'] = did_result['did']
    FARDINHO['key'] = did_result['key']

    # Store the DID and key using Askar
    store = AskarStore()
    await store.open()
    await store.insert(FARDINHO['did'], FARDINHO['key'])
    await store.close()

    # Add the fardinho to the pool
    pool_.append(FARDINHO)

async def create_uba(pool_, uba_data, trustee):
    global cont_Uba
    cont_Uba += 1

    print(f"\nCriando UBA {cont_Uba} - Cadastre")

    UBA = {
        'name': uba_data['name'],
        # Add any other data from uba_data as needed
    }

    # Create a new DID for the uba
    did_result = DIDKit.generate25519_key()
    UBA['did'] = did_result['did']
    UBA['key'] = did_result['key']

    # Store the DID and key using Askar
    store = AskarStore()
    await store.open()
    await store.insert(UBA['did'], UBA['key'])
    await store.close()

    # Add the uba to the pool
    pool_.append(UBA)
    

async def create_transaction(sender, receiver, custo_far, quant_far):
    global cont_Tran
    cont_Tran += 1

    amount = custo_far * quant_far

    # Create the transaction
    transaction = {
        'from': sender['did'],
        'to': receiver['did'],
        'value': amount,
        'data': {
            'quant_far': quant_far,
            'custo_far': custo_far,
        },
    }

    # Convert the transaction to a JSON string
    transaction_json = json.dumps(transaction)

    # Create a request for the transaction
    request = await ledger.build_attrib_request(sender['did'], receiver['did'], None, transaction_json, None)

    # Sign the request with the sender's key
    signed_request = await ledger.sign_request(sender['wallet'], sender['did'], request)

    # Send the request to the ledger
    response = await ledger.submit_request(sender['pool'], signed_request)

    print(f"Transação {cont_Tran} enviada com sucesso. Resposta: {response}")

async def run():
    pool_ = {
        'name': 'pool1'
    }

    print("Abrindo Pool Ledger: {}".format(pool_['name']))

    pool_['genesis_txn_path'] = "/home/indy/sandbox/cottontrust/genesis.txn"
    pool_['config'] = json.dumps({"genesis_txn": str(pool_['genesis_txn_path'])})

    await pool.set_protocol_version(2)

    try:
        await pool.create_pool_ledger_config(pool_['name'], pool_['config'])
    except error.IndyError as ex:
        if ex.error_code == error.ErrorCode.PoolLedgerConfigAlreadyExistsError:
            pass

    pool_handle = await pool.open_pool_ledger(pool_['name'], None)

    print("Pool Ledger aberto com sucesso.")

    with open('teste.json', 'r') as file:
        teste_data = json.load(file)

    trustee = {
        'name': 'trustworthy_agent',
        'seed': '000000000000000000000000Trustee1',
        'wallet_config': json.dumps({'id': teste_data['wallet_config']}),
        'wallet_credentials': json.dumps({'key': teste_data['wallet_credentials']}),
        'pool': pool_['handle'],
        'role': 'TRUSTEE'
    }

    # Criando Trustee
    await create_wallet(trustee)
    (trustee['did'], trustee['key']) = await did.create_and_store_my_did(trustee['wallet'], json.dumps({"seed": trustee['seed']}))
    await setup_identity(trustee,trustee)


    # UBAS -----------------------------------------------------------------------------------

    with open('ubas.json', 'r') as file:
        try:
            ubas_data = json.load(file)
        except json.JSONDecodeError:
            print("Arquivo UBA esta vazio.\n")
            ubas_data = []

    if ubas_data:
        for uba_data in ubas_data:
            time_uba = time.time()
            await create_uba(pool_, uba_data, trustee)
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
            await create_fardinho(pool_, fardinho_data)

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
            await create_cliente(pool_, cliente_data, trustee)
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

    # TEMPOS --------------------------------------------------------------------------------------------
    print("Escrevendo no arquivo CSV...")
    print(f"Tempos de transacao: {tempos_transacao}")
    print(f"Tempos de criacao: {tempo_criacao}")

    with open('tempos.csv', 'a', newline='') as file:  # Abrir arquivo no modo de anexação
        writer = csv.writer(file)
        if not os.path.exists('tempos.csv') or os.stat('tempos.csv').st_size == 0:  # Se o arquivo não existir ou estiver vazio
            writer.writerow(["Quant. De Entidades:", "Tempo de Transacao:", "Tempo de Criacao:"])  # Escrever cabeçalho
        for t, tc in zip(tempos_transacao, tempo_criacao):
            writer.writerow(["100", t, tc])  # Escrever dados
        writer.writerow([])
print("Concluído.")

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
