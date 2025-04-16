import asyncio
import requests
import json
import time
import csv
import random
import os
from indy import pool, wallet, did, ledger
from indy.error import ErrorCode, IndyError

UBAs = []
Bale = []
Clients = []


time_transaction = []
time_create = []

transacoes_enviadas = []

cont_Uba = 0
cont_Bale = 0
cont_Cli = 0

cont_Tran = 0

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

async def create_pools(pools_config):
    """
    Cria e abre os pools com base nas configurações fornecidas.

    :param pools_config: Lista de dicionários com as chaves "name" e "genesis_txn_path".
    :return: Dicionário onde as chaves são os nomes dos pools e os valores são os handles abertos.
    """
    pools = {}
    # Define a versão do protocolo para o Indy
    await pool.set_protocol_version(2)
    
    for config in pools_config:
        config_json = json.dumps({"genesis_txn": config["genesis_txn_path"]})
        try:
            # Apaga a configuração antiga, se existir
            await pool.delete_pool_ledger_config(config["name"])
            print(f"Configuracao do pool '{config['name']}' deletada com sucesso.")
        except Exception as ex:
            # Só avisa, não para a execução se o pool não existir
            print(f"Nao foi possivel deletar o pool '{config['name']}': {ex}")
        try:
            print(f"Criando nova pool: '{config['name']}'")
            await pool.create_pool_ledger_config(config["name"], config_json)
        except Exception as ex:
            from indy.error import ErrorCode, IndyError
            if isinstance(ex, IndyError) and ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
                print(f"Pool '{config['name']}' já existe.")
            else:
                raise ex
        print("Foda, pica.\n")
        handle = await pool.open_pool_ledger(config["name"], None)
        pools[config["name"]] = handle
        print(f"Configuracao do pool '{config['name']}' aberta com sucesso\n")

    return pools

async def reenviar_transacao_para_outro_pool(transacao, novo_pool_handle, wallet_assinante):
    """
    Reenvia a transação registrada (NYM request) para um novo pool.

    :param transacao: Dicionário com chaves "did_enviada", "verkey_enviada" e "did_assinante".
    :param novo_pool_handle: Handle do novo pool.
    :param wallet_assinante: Wallet que contém a identidade que vai assinar a transação.
    :return: Resposta do ledger em formato de dicionário.
    """
    nym_req = await ledger.build_nym_request(
        transacao["did_assinante"],
        transacao["did_enviada"],
        transacao["verkey_enviada"],
        None,
        None
    )
    response = await ledger.sign_and_submit_request(novo_pool_handle, wallet_assinante, transacao["did_assinante"], nym_req)
    response_dict = json.loads(response)
    print(f'[NOVO POOL] Response: {response_dict}\n')
    return response_dict


      
async def delete_wallet(wallet_config, wallet_credentials):
    try:
        await wallet.delete_wallet(wallet_config, wallet_credentials)
        print("Wallet cleanup successful.")
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletNotFoundError:
            print("No wallet found for cleanup. Proceeding...")
        else:
            raise ex 
      
      
async def create_wallet(Entity):
    print("\"{}\" -> Creating  wallet(wallet)".format(Entity['name']))

    await delete_wallet(Entity['wallet_config'], Entity['wallet_credentials'])


    try:
        await wallet.create_wallet(Entity['wallet_config'],
                                   Entity['wallet_credentials'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            pass
        else:
            raise ex

    Entity['wallet'] = await wallet.open_wallet(Entity['wallet_config'],
                                                  Entity['wallet_credentials'])
    
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

        'seed': create_seed(cont_Cli, client_data['name']),
        "balance": client_data['balance'],
        "req_bale": client_data['req_bale'],
        "quant_bale": client_data['quant_bale']

    }

    await create_wallet(CLIENT)
    CLIENT["did_info"] = json.dumps({'seed': CLIENT['seed']})

    CLIENT['did'], CLIENT['key'] = await did.create_and_store_my_did(CLIENT['wallet'], CLIENT['did_info']) 

    await setup_identity(CLIENT, trustee)
    Clients.append(CLIENT)  
    

async def create_bale(pool_, bale_data):
    global cont_Bale
    cont_Bale += 1
    

    print(f"Creating bale {cont_Bale} - Sign up")


    BALE = {
        'name': bale_data['name'],
        'Bale Identifier': bale_data['Bale Identifier'],
        'Farm Identifier': bale_data['Farm Identifier'],
        'UBA Identifier': bale_data['UBA Identifier'],
        'Harvest Season': bale_data['Harvest Season'],
        'Plot': bale_data['Plot'],
        'Harvest Date': bale_data['Harvest Date'],
        'Seed Product': bale_data['Seed Product'],
        'Seed Lot': bale_data['Seed Lot'],
        'Weight': bale_data['Weight'],
        'wallet_config': json.dumps({'id': bale_data['wallet_config']}),
        'wallet_credentials': json.dumps({'key': bale_data['wallet_credentials']}),
        'pool': pool_['handle'],

        'seed': create_seed(cont_Bale, bale_data['name']),
        "balance": 1000

    }

    await create_wallet(BALE)
    BALE["did_info"] = json.dumps({'seed': BALE['seed']})
    BALE['did'], BALE['key'] = await did.create_and_store_my_did(BALE['wallet'], BALE['did_info'])

    Bale.append(BALE) 

async def create_uba(pool_, uba_data, trustee):
    global cont_Uba
    cont_Uba += 1
    

    print(f"\Creating UBA {cont_Uba} - Sign Up")
    


    UBA = {
        'name': uba_data['name'],
        'UBA registry code': uba_data['UBA Registry Code'],
        'CNPJ': uba_data['CNPJ'],
        'Address - Street': uba_data['Address - Street'],
        'Address - Neighborhood': uba_data['Address - Neighborhood'],
        'Address - City': uba_data['Address - City'],
        'Address - State': uba_data['Address - State'],
        'Address - Country': uba_data['Address - Country'],
        'wallet_config': json.dumps({'id': uba_data['wallet_config']}),
        'wallet_credentials': json.dumps({'key': uba_data['wallet_credentials']}),
        'pool': pool_['handle'],

        'seed': create_seed(cont_Uba, uba_data['name']),
        "balance": uba_data['balance'],
        "bale_price": uba_data['bale_price'],#add
        "quant_bale": uba_data['quant_bale'] #add
    }

    
    await create_wallet(UBA)

    UBA["did_info"] = json.dumps({'seed': UBA['seed']})
    UBA['did'], UBA['key'] = await did.create_and_store_my_did(UBA['wallet'], UBA['did_info'])

    await setup_identity(UBA, trustee)
    UBAs.append(UBA)
    
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
        },
        {
            "name": "sandbox2",
            "genesis_txn_path": "/home/indy/sandbox/cottontrust_milton/cottontrust/txn/genesis2.txn"
        }
    ]
    
    
    # Cria e abre os pools
    #print("comecei a fazer a putaria\n")
    pools = await create_pools(pools_config)
    #print("voltei pra ca, tentando abrir o pool de verdade agora -1 ainda\n")
    # Define o pool principal para as operações iniciais.
    main_pool_name = "sandbox"
    pool_ = {"name": main_pool_name, "handle": pools[main_pool_name]}
    #print("voltei pra ca, tentando abrir o pool de verdade agora\n")
    # --- Trecho referente à criação de Trustee, UBAs, Bale, Clients e transações ---
    # Exemplo: Trustee
    with open('models/test.json', 'r') as file:
        teste_data = json.load(file)
    
    trustee = {
        'name': 'trustworthy_agent',
        'seed': '000000000000000000000000Trustee1',
        'wallet_config': json.dumps({'id': teste_data['wallet_config']}),
        'wallet_credentials': json.dumps({'key': teste_data['wallet_credentials']}),
        'pool': pool_['handle'],
        'role': 'TRUSTEE'
    }
    
    # Criação do trustee
    await create_wallet(trustee)
    (trustee['did'], trustee['key']) = await did.create_and_store_my_did(trustee['wallet'], json.dumps({"seed": trustee['seed']}))
    await setup_identity(trustee, trustee)
    
    # Processamento dos modelos (UBAs, Bale, Clients)
    with open('models/ubas.json', 'r') as file:
        try:
            ubas_data = json.load(file)
        except json.JSONDecodeError:
            print("UBA file empty.\n")
            ubas_data = []
    if ubas_data:
        for uba_data in ubas_data:
            time_uba = time.time()
            await create_uba(pool_, uba_data, trustee)
            endtime_uba = time.time()
            time_create.append(endtime_uba - time_uba)
    
    with open('models/bale.json', 'r') as file:
        try:
            bale_data = json.load(file)
        except json.JSONDecodeError:
            print("Bale file is empty.\n")
            bale_data = []
    if bale_data:
        for bale_item in bale_data:
            await create_bale(pool_, bale_item)
    
    with open('models/clients.json', 'r') as file:
        try:
            clients_data = json.load(file)
        except json.JSONDecodeError:
            print("Client file is empty.\n")
            clients_data = []
    if clients_data:
        for client_data in clients_data:
            time_cli = time.time()
            await create_client(pool_, client_data, trustee)
            endtime_cli = time.time()
            time_create.append(endtime_cli - time_cli)
    
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
    for pool_name, pool_handle in pools.items():
        if pool_name == main_pool_name:
            continue  # Pula o pool usado nas operações iniciais
        print(f"Reenviando transacoes para {pool_name}...")
        # Se o mesmo trustee pode ser usado para assinar, passe o mesmo wallet
        for transacao in transacoes_enviadas:
            await reenviar_transacao_para_outro_pool(transacao, pool_handle, trustee['wallet'])
    

    # TIMES --------------------------------------------------------------------------------------------
    print("Writing on CSV file...")
    print(f"Transaction time: {time_transaction}")
    print(f"Creation time: {time_create}")

    with open('time_data.csv', 'a', newline='') as file: 
        writer = csv.writer(file)
        if not os.path.exists('time_data.csv') or os.stat('time_data.csv').st_size == 0:  
            writer.writerow(["Quant. of Entitys:", "Transaction time:", "Creation time:"])  
        for t, tc in zip(time_transaction, time_create):
            writer.writerow(["100", t, tc])  
        writer.writerow([])
print("Done.")

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
