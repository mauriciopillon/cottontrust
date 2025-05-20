import asyncio
import requests
import json
import time
import csv
import random
import os
import uuid
from datetime import datetime
from indy import pool, wallet, did, ledger
from indy.error import ErrorCode, IndyError

UBAs = []
Bales = []
Clients = []


time_transaction = []
time_create = []
raw_tx_metrics = []

transacoes_enviadas = []

cont_Uba = 0
cont_Bale = 0
cont_Cli = 0

cont_Tran = 0

def save_metrics_to_csv(filename="raw_tx_metrics.csv"):
    if not raw_tx_metrics:
        print(" Nenhuma metrica registrada para salvar!")
        return

    headers = ["pool", "operation", "tx_time_sec", "tx_size_bytes", "timestamp"]
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for record in raw_tx_metrics:
            writer.writerow(record)

    print(f"Metricas salvas com sucesso em {filename}")



async def setup_identity(identity, trustee):
    did_safe = 'V4SGRU86Z58d6TV7PBUe6f'
    verkey_safe = '~CoRER63DVYnWZtK8uAzNbx' 
    (identity['did'], identity['key']) = await did.create_and_store_my_did(identity['wallet'], "{}")

    # Build NYM request
    nym_req = await ledger.build_nym_request(
        did_safe,               # Quem assina
        identity['did'],        # DID que está sendo adicionada
        identity['key'],        # Verkey
        None,
        None
    )

    tx_size_bytes = len(nym_req.encode('utf-8'))
    
    # Envia a transação
    response = await ledger.sign_and_submit_request(identity['pool'], trustee['wallet'], did_safe, nym_req)
    response_dict = json.loads(response)
    print(f'response found: {response_dict}\n')

    # Captura o ID da transação (txnMetadata > txnId)
    txn_id = response_dict.get("result", {}).get("txnMetadata", {}).get("txnId", "desconhecido")

    # Armazena as informações da transação em uma estrutura
    transacoes_enviadas.append({
        "txn_id": txn_id,
        "did_enviada": identity['did'],
        "verkey_enviada": identity['key'],
        "did_assinante": did_safe
    })
    

    return tx_size_bytes
    
    # A resposta Indy costuma ter este formato:
    # {
    #   "op": "REPLY",
    #   "result": {
    #     "reqId": <numero>,
    #     "txn": {...},
    #     "txnMetadata": {"seqNo": <numero>, "txnId": <ID da transação>},
    #     ...
    #   }
    # }
    #

async def create_pools(pools_config: list):
    pools = []
    for config in pools_config:
        name = config["name"]
        genesis_path = config["genesis_txn_path"]

        # Indy wants exactly {"genesis_txn": "/path/to/file"}
        pool_config = { "genesis_txn": genesis_path }
        config_json = json.dumps(pool_config)

        # Try deleting old config; ignore *all* IndyErrors here
        try:
            await pool.delete_pool_ledger_config(name)
            print(f"Deleted existing pool config '{name}'")
        except IndyError:
            # Could not delete–either it never existed or
            # some other Indy error happened. We ignore it.
            pass

        # Now create the new pool ledger config
        try:
            await pool.create_pool_ledger_config(name, config_json)
            print(f"Created pool config '{name}' with: {config_json}")
        except IndyError as ex:
            # Something really went wrong on create
            print(f"Failed to create pool '{name}':", ex)
            raise

        # Finally open the pool
        handle = await pool.open_pool_ledger(name, None)
        print(f"Opened pool '{name}', handle={handle}")
        pools.append({ "name": name, "handle": handle })

    return pools

async def reenviar_transacao_para_outro_pool(transacao, novo_pool_handle, wallet_assinante, pool_name):
    """
    Reenvia a transação registrada (NYM request) para um novo pool e registra
    métricas "cruas" (tempo de execução e tamanho do payload).

    :param transacao: Dicionário com chaves "did_enviada", "verkey_enviada" e "did_assinante".
    :param novo_pool_handle: Handle do novo pool.
    :param wallet_assinante: Wallet que contém a identidade que vai assinar a transação.
    :param pool_name: Nome do pool para registro na métrica.
    :return: Resposta do ledger em formato de dicionário.
    """
    # Constrói o NYM request completo
    nym_req = await ledger.build_nym_request(
        transacao["did_assinante"],
        transacao["did_enviada"],
        transacao["verkey_enviada"],
        None,
        None
    )
    # Calcula o tamanho do payload da transação
    tx_size_bytes = len(nym_req.encode('utf-8'))
    
    # Mede o tempo para enviar a transação ao novo pool
    start = time.time()
    response = await ledger.sign_and_submit_request(novo_pool_handle, wallet_assinante, transacao["did_assinante"], nym_req)
    end = time.time()
    duration = end - start
    
    response_dict = json.loads(response)
    print(f'[NOVO POOL: {pool_name}] Response: {response_dict}\n')
    
    # Registra as informações na lista global (raw_tx_metrics deve ter sido definida globalmente)
    raw_tx_metrics.append({
        "pool": pool_name,
        "operation": "reenviar_transacao",
        "tx_time_sec": duration,
        "tx_size_bytes": tx_size_bytes,
        "timestamp": datetime.now().isoformat()
    })
    
    return response_dict


      
async def delete_wallet(wallet_config: dict, wallet_credentials: dict):
    # 1) JSON‑encode here:
    cfg = json.dumps(wallet_config)
    creds = json.dumps(wallet_credentials)
    print(f"Deleting wallet with config={cfg} creds={creds}")
    try:
        await wallet.delete_wallet(cfg, creds)
        print("Wallet cleanup successful.")
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletNotFoundError:
            print("No wallet found for cleanup. Continuing.")
        else:
            print("delete_wallet failed:", ex)
            raise

async def create_wallet(entity: dict):
    config_json = json.dumps(entity['wallet_config'])
    creds_json  = json.dumps(entity['wallet_credentials'])

    try:
        await delete_wallet(entity['wallet_config'], entity['wallet_credentials'])
    except IndyError:
        pass  # wallet not found — tudo bem

    try:
        await wallet.create_wallet(config_json, creds_json)
        print("Wallet created.")
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            print("Wallet already exists.")
        else:
            raise

    #atribui o handle no dicionário
    entity['wallet'] = await wallet.open_wallet(config_json, creds_json)
    
def create_seed(counter, name):
        seed =  str(name) + str(counter) + 'A0000000000000000000000000000000000' 
        return seed[:32]

async def create_client(pool_, client_data, trustee):
    global cont_Cli
    cont_Cli += 1
    

    print(f"\nCreating Clients {cont_Cli} - Sign up")


    CLIENT = {
        'name': client_data['name'],
        'Address - Street': client_data['Address - Street'],
        'Address - Neighborhood': client_data['Address - Neighborhood'],
        'Address - City': client_data['Address - City'],
        'Address - State': client_data['Address - State'],
        'Address - Country': client_data['Address - Country'],
        'wallet_config': json.dumps({'id': client_data['wallet_config']}),
        'wallet_credentials': json.dumps({'key': client_data['wallet_credentials']}),
        'pool': pool_['handle'],
        'pool_name': pool_['name'],
        'seed': create_seed(cont_Cli, client_data['name']),
        "balance": client_data['balance'],
        "req_bale": client_data['req_bale'],
        "quant_bale": client_data['quant_bale']

    }
    start = time.time()
    await create_wallet(CLIENT)
    CLIENT["did_info"] = json.dumps({'seed': CLIENT['seed']})

    CLIENT['did'], CLIENT['key'] = await did.create_and_store_my_did(CLIENT['wallet'], CLIENT['did_info']) 

    tx_size = await setup_identity(CLIENT, trustee)
    Clients.append(CLIENT)  

    end = time.time()
    duration = end - start
    
    
    
    # Registra um snapshot da data/hora
    timestamp = datetime.now().isoformat()
    
    # Adiciona um registro à lista global
    raw_tx_metrics.append({
        "pool": CLIENT['pool_name'],
        "operation": "create_client",
        "tx_time_sec": duration,
        "tx_size_bytes": tx_size,
        "timestamp": timestamp
    })
    print(f"Cliente criado em {duration:.3f} s, payload size: {tx_size} bytes")

    

async def create_bale(pool_, bale_data, trustee):
    global cont_Bale
    cont_Bale += 1

    print(f"\nCreating Bale {cont_Bale} - Sign Up")
    wallet_id = f"wallet_bale_{bale_data['id']}"
    wallet_key = f"key_{bale_data['id']}"  # fixo por id


    BALE = {
        'id':               bale_data['id'],
        'beneficiamento_id': bale_data['id_beneficiamento'],
        'product_id':       bale_data['id_produto'],
        'description':      bale_data['produto_descricao'],
        'gross_weight':     bale_data['peso_bruto'],
        'net_weight':       bale_data['peso_liquido'],
        'production_time':  bale_data['data_hora_producao'],
        'wallet_config':       {'id': wallet_id},
        'wallet_credentials':  {'key': wallet_key},
        'pool': pool_['handle'],
        'pool_name': pool_['name'],   # Armazena o nome do pool para os registros
        'seed': create_seed(cont_Bale, bale_data['id_produto']),
    }

    # Início da métrica de tempo
    start = time.time()

    # Cria a wallet
    await create_wallet(BALE)

    # Gera DID
    BALE["did_info"] = json.dumps({'seed': BALE['seed']})
    BALE['did'], BALE['key'] = await did.create_and_store_my_did(BALE['wallet'], BALE['did_info'])

    # Executa a transação de registro da bale e captura o tamanho do payload
    tx_size = await setup_identity(BALE, trustee)

    # Adiciona à lista global de bales
    Bales.append(BALE)

    # Fim da métrica de tempo
    end = time.time()
    duration = end - start  # tempo da operação, em segundos

    # Timestamp ISO para o log
    timestamp = datetime.now().isoformat()

    # Registro da métrica
    print("Registrando metrica:", BALE['pool_name'], duration, tx_size)
    raw_tx_metrics.append({
        "pool": BALE['pool_name'],
        "operation": "create_bale",
        "tx_time_sec": duration,
        "tx_size_bytes": tx_size,
        "timestamp": timestamp
    })

    print(f"Bale criada em {duration:.3f} s, payload size: {tx_size} bytes")

async def create_uba(pool_, uba_data, trustee):
    global cont_Uba
    cont_Uba += 1

    print(f"\nCreating UBA {cont_Uba} - Sign Up")
    wallet_id = f"wallet_uba_{uba_data['id']}"
    wallet_key = f"key_{uba_data['id']}"  # fixo por id
    
    UBA = {
        'id':                  uba_data['id'],
        'code':                uba_data['codigo'],
        'description':         uba_data['descricao'],
        'location':            uba_data['local'],
        'company_id':          uba_data['id_empresa'],

        
        'wallet_config':       {'id':  wallet_id},
        'wallet_credentials':  {'key': wallet_key},

        'pool':                pool_['handle'],
        'pool_name':           pool_['name'],

        # use 'codigo' (or another existing field) for your seed
        'seed':                create_seed(cont_Uba, uba_data['codigo']),
    }
    
    start = time.time()
    
    await create_wallet(UBA)
    
    UBA["did_info"] = json.dumps({'seed': UBA['seed']})
    UBA['did'], UBA['key'] = await did.create_and_store_my_did(UBA['wallet'], UBA['did_info'])
    
    tx_size = await setup_identity(UBA, trustee)
    UBAs.append(UBA)
    
    end = time.time()
    duration = end - start  # tempo da operação, em segundos
    
    # Calcula o tamanho do payload (ex: o JSON usado para did_info)
    
    # Registra um snapshot da data/hora
    timestamp = datetime.now().isoformat()

    print("Registrando metrica:", UBA['pool_name'], duration, tx_size)
    
    # Adiciona um registro à lista global
    raw_tx_metrics.append({
        "pool": UBA['pool_name'],
        "operation": "create_uba",
        "tx_time_sec": duration,
        "tx_size_bytes": tx_size,
        "timestamp": timestamp
    })
    
    print(f"UBA criada em {duration:.3f} s, payload size: {tx_size} bytes")

# FUNCTION NOT BEING CURRENTLY USED
async def create_transaction(sender, receiver, bale_cost, quant_bale):
    global cont_Tran
    cont_Tran += 1

    amount = bale_cost * quant_bale
    print("--------------------------------------------")
    print(f"Starting transaction {cont_Tran}:")
    print(f"Current balance of {sender['name']}: R${sender['balance']},00")
    print(f"Current balance of {receiver['name']}: R${receiver['balance']},00")
    print(f"Quantity of bales available in {receiver['name']}: {receiver['quant_bale']}")
    print(f"Quantity of bales {sender['name']} wants to buy: {quant_bale}")
    print(f"Price of each bale: R${bale_cost},00")
    print(f"Total transaction value: R${amount},00")


    start_time = time.time()

    if sender['balance'] < amount:
        print(f"{sender['name']} has insufficient funds")
        return

    sender['balance'] -= amount

    sender['quant_bale'] += quant_bale

    sender_attr_req = await ledger.build_attrib_request(sender['did'], sender['did'], None, json.dumps({'balance': sender['balance'], 'quant_bale': sender['quant_bale']}), None)

    await ledger.sign_and_submit_request(sender['pool'], sender['wallet'], sender['did'], sender_attr_req)

    receiver['balance'] += amount

    receiver['quant_bale'] -= quant_bale

    receiver_attr_req = await ledger.build_attrib_request(receiver['did'], receiver['did'], None, json.dumps({'balance': receiver['balance'], 'quant_bale': receiver['quant_bale']}), None)

    await ledger.sign_and_submit_request(receiver['pool'], receiver['wallet'], receiver['did'], receiver_attr_req)

    end_time = time.time()
    duration = end_time - start_time
    print(f"\nThe transaction took {duration} secs\n")
    time_transaction.append(duration)

    print(f"Sucessful Transaction: {sender['name']} sent R${amount},00 to {receiver['name']} and received {quant_bale} bales")
    print(f"Current balance {sender['name']}: R${sender['balance']},00 and {sender['quant_bale']} bales")
    print(f"Current balance {receiver['name']}: R${receiver['balance']},00 and {receiver['quant_bale']} bales")
    print("--------------------------------------------")


async def run():
    
    
    #FLUXO DO QUE O CÓDIGO FAZ:
    #1: CRIAR OU ACESSAR UM POOL
    #2: TER UMA DID "TRUSTEE" PARA VALIDAR NOSSAS TRANSAÇÕES
    #3: LER OS DADOS (NO NOSSO CASO, AS UBAS) E CARREGAR EM MEMÓRIA
    #   3.1: CRIAR UMA CARTEIRA PARA NOSSOS DADOS (UMA FORMA DE RECONHECER NA BLOCKCHAIN)
    #   3.2: ENVIAR REQUISIÇÃO PARA SER ASSINADA (USAR DID TRUSTEE E DID DA CARTEIRA NOVA)
    #4: INDY.LEDGER_BUILD_NYM_REQ E LEDGER.SIGN_AND_SUBMIT_REQUEST
    #5: EM TEORIA, TUDO ISSO DANDO CERTO, TEMOS UMA ESCRITA NA BLOCKCHAIN
    
    # Configurações dos pools (atualize os caminhos para os arquivos gênese conforme necessário)
#    pools_config = [
#        {
#            "name": "sandbox1",
#            "genesis_txn_path": "/home/indy/sandbox/cottontrust_milton/cottontrust/txn/genesis1.txn"
#        },
#        {
#            "name": "sandbox2",
#            "genesis_txn_path": "/home/indy/sandbox/cottontrust_milton/cottontrust/txn/genesis2.txn"
#        },
#        {
#            "name": "sandbox3",
#            "genesis_txn_path": "/home/indy/sandbox/cottontrust_milton/cottontrust/txn/genesis3.txn"
#        },
#        {
#            "name": "sandbox4",
#            "genesis_txn_path": "/home/indy/sandbox/cottontrust_milton/cottontrust/txn/genesis4.txn"
#        }
#    ]
    
    pools_config = [
        {
            "name": "sandbox",
            "genesis_txn_path": "/home/indy/sandbox/cottontrust_milton/cottontrust/txn/genesis1.txn"
        }
    ]
    
    await pool.set_protocol_version(2)

    # Cria e abre os pools
    pools = await create_pools(pools_config)

    # Transforma a lista em um dicionário: {'sandbox1': handle1, 'sandbox2': handle2, ...}
    pool_map = {p["name"]: p["handle"] for p in pools}

    # Define o nome do pool principal
    main_pool_name = "sandbox"  # ou "sandbox2", etc. conforme definido no pools_config

    # Usa o dicionário para obter o handle
    pool_ = {"name": main_pool_name, "handle": pool_map[main_pool_name]}
    
    
    # --- Trecho referente à criação de Trustee, UBAs, Bale, Clients e transações ---
    # Exemplo: Trustee
    with open('models/test.json', 'r') as file:
        teste_data = json.load(file)
    
    trustee = {
        'name': 'trustworthy_agent',
        'seed': '000000000000000000000000Trustee1',
        'wallet_config': {'id': teste_data['wallet_config']},
        'wallet_credentials': {'key': teste_data['wallet_credentials']},
        'pool': pool_['handle'],
        'role': 'TRUSTEE'
    }
    

    
    # Criação do trustee
    await create_wallet(trustee)
    (trustee['did'], trustee['key']) = await did.create_and_store_my_did(trustee['wallet'], json.dumps({"seed": trustee['seed']}))
    await setup_identity(trustee, trustee)
    
    # Processamento dos modelos (UBAs, Bale, Clients)
    ubas_data = []
    with open('models/ubas.json', 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            try:
                uba = json.loads(line)
            except json.JSONDecodeError:
                print("Skipping malformed line:", line)
                continue
            ubas_data.append(uba)
            
    if ubas_data:
        for uba_data in ubas_data:
            await create_uba(pool_, uba_data, trustee)
    
    bales_data = []
    with open('models/bales.json', 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            try:
                bale = json.loads(line)
            except json.JSONDecodeError:
                print("Skipping malformed line:", line)
                continue
            bales_data.append(bale)

    if bales_data:
        for bale_data in bales_data:
            await create_bale(pool_, bale_data, trustee)

#    with open('models/clients.json', 'r') as file:
#        try:
#            clients_data = json.load(file)
#        except json.JSONDecodeError:
#            print("Client file is empty.\n")
#            clients_data = []
#    if clients_data:
#        for client_data in clients_data:
#            await create_client(pool_, client_data, trustee)
    
    # Processa transações, conforme o seu fluxo atual
    if UBAs and Clients:
        num_trans = 4  # Quantidade de transações desejada
        for _ in range(num_trans):
            sender = random.choice(Clients)
            receiver = random.choice(UBAs)
            bale_cost = receiver['bale_price']
            quant_bale = sender['req_bale']
            await create_transaction(sender, receiver, bale_cost, quant_bale)
    
    # --- Replicação das Transações para os Demais Pools ---
    print("Replicando transacoes para os demais pools:")
    for pool_name, pool_handle in pool_map.items():
        if pool_name == main_pool_name:
            continue
        print(f"Reenviando transacoes para {pool_name}...")
        for transacao in transacoes_enviadas:
            await reenviar_transacao_para_outro_pool(transacao, pool_handle, trustee['wallet'], pool_name)   

    # TIMES --------------------------------------------------------------------------------------------
#    print("Writing on CSV file...")
#    print(f"Transaction time: {time_transaction}")
#    print(f"Creation time: {time_create}")
#
#    with open('time_data.csv', 'a', newline='') as file: 
#        writer = csv.writer(file)
#        if not os.path.exists('time_data.csv') or os.stat('time_data.csv').st_size == 0:  
#            writer.writerow(["Quant. of Entitys:", "Transaction time:", "Creation time:"])  
#        for t, tc in zip(time_transaction, time_create):
#            writer.writerow(["100", t, tc])  
#        writer.writerow([])
    save_metrics_to_csv()
    print("Done.")

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
