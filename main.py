import asyncio
import json
import time

from indy import pool, wallet, did
from indy.error import ErrorCode, IndyError

UBAs = []
Fardinhos = []
Clientes = []

cont_Uba = 0
cont_Far = 0
cont_Cli = 0

async def create_wallet(Entidade):
    print("\"{}\" -> Criando ou Abrindo Carteira(wallet)".format(Entidade['name']))
    try:
        await wallet.create_wallet(Entidade['wallet_config'],
                                   Entidade['wallet_credentials'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.WalletAlreadyExistsError:
            pass
        else:
            raise ex

    Entidade['wallet'] = await wallet.open_wallet(Entidade['wallet_config'],
                                                  Entidade['wallet_credentials'])
    
def create_seed(contador, nome):
        seed =  str(nome) + str(contador) + 'A0000000000000000000000000000000000' 
        return seed[:32]

async def create_cliente(pool_, cliente_data):
    global cont_Cli
    cont_Cli += 1
    start_time = time.time()
    
    print(f"Criando Clientes {cont_Cli} - Cadastre")

    CLIENTE = {
        'name': cliente_data['name'],
        'Endereco - Rua': cliente_data['Endereco - Rua'],
        'Endereco - Bairro': cliente_data['Endereco - Bairro'],
        'Endereco - Cidade': cliente_data['Endereco - Cidade'],
        'Endereco - Estado': cliente_data['Endereco - Estado'],
        'Endereco - Pais': cliente_data['Endereco - Pais'],
        'wallet_config': json.dumps({'id': cliente_data['wallet_config']}),
        'wallet_credentials': json.dumps({'key': cliente_data['wallet_credentials']}),
        'pool': pool_['handle'],
        'seed': create_seed(cont_Cli, cliente_data['name'])
    }

    await create_wallet(CLIENTE)
    CLIENTE["did_info"] = json.dumps({'seed': CLIENTE['seed']})
    CLIENTE['did'], CLIENTE['key'] = await did.create_and_store_my_did(CLIENTE['wallet'], CLIENTE['did_info'])
    Clientes.append(CLIENTE)
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Tempo de criacao do {CLIENTE['name']}: {total_time} segundos")

async def create_fardinho(pool_, fardinho_data):
    global cont_Far
    cont_Far += 1
    start_time = time.time()

    print(f"Criando Fardinho {cont_Far} - Cadastre")

    FARDINHO = {
        'name': fardinho_data['name'],
        'Identificador do Fardinho': fardinho_data['Identificador do Fardinho'],
        'Identificador da Fazenda': fardinho_data['Identificador da Fazenda'],
        'Identificador da UBA': fardinho_data['Identificador da UBA'],
        'Safra': fardinho_data['Safra'],
        'Talhao': fardinho_data['Talhao'],
        'Data da Colheita': fardinho_data['Data da Colheita'],
        'Produto da Semente': fardinho_data['Produto da Semente'],
        'Lote da Semente': fardinho_data['Lote da Semente'],
        'Peso': fardinho_data['Peso'],
        'wallet_config': json.dumps({'id': fardinho_data['wallet_config']}),
        'wallet_credentials': json.dumps({'key': fardinho_data['wallet_credentials']}),
        'pool': pool_['handle'],
        'seed': create_seed(cont_Far, fardinho_data['name']) 
    }

    await create_wallet(FARDINHO)
    FARDINHO["did_info"] = json.dumps({'seed': FARDINHO['seed']})
    FARDINHO['did'], FARDINHO['key'] = await did.create_and_store_my_did(FARDINHO['wallet'], FARDINHO['did_info'])
    Fardinhos.append(FARDINHO)
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Tempo de criacao do {FARDINHO['name']}: {total_time} segundos")

async def create_uba(pool_, uba_data):
    global cont_Uba
    cont_Uba += 1
    start_time = time.time()

    print(f"Criando UBA {cont_Uba} - Cadastre")
    
    UBA = {
        'name': uba_data['name'],
        'Codigo de Registro da UBA': uba_data['Codigo de Registro da UBA'],
        'CNPJ': uba_data['CNPJ'],
        'Endereco - Rua': uba_data['Endereco - Rua'],
        'Endereco - Bairro': uba_data['Endereco - Bairro'],
        'Endereco - Cidade': uba_data['Endereco - Cidade'],
        'Endereco - Estado': uba_data['Endereco - Estado'],
        'Endereco - Pais': uba_data['Endereco - Pais'],
        'wallet_config': json.dumps({'id': uba_data['wallet_config']}),
        'wallet_credentials': json.dumps({'key': uba_data['wallet_credentials']}),
        'pool': pool_['handle'],
        'seed': create_seed(cont_Uba, uba_data['name'])
    }


    await create_wallet(UBA)
    UBA["did_info"] = json.dumps({'seed': UBA['seed']})
    UBA['did'], UBA['key'] = await did.create_and_store_my_did(UBA['wallet'], UBA['did_info'])
    UBAs.append(UBA)
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Tempo de criacao do {UBA['name']}: {total_time} segundos")


async def run():

    start_time = time.time()

    pool_ = {
        'name': 'pool1'
    }

    print("Open Pool Ledger: {}".format(pool_['name']))
    pool_['genesis_txn_path'] = "/home/indy/UBA-7.0/pool1.txn"
    pool_['config'] = json.dumps({"genesis_txn": str(pool_['genesis_txn_path'])})

    await pool.set_protocol_version(2)

    try:
        await pool.create_pool_ledger_config(pool_['name'], pool_['config'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            pass
    pool_['handle'] = await pool.open_pool_ledger(pool_['name'], None)

    #UBAS -----------------------------------------------------------------------------------

    with open('ubas.json', 'r') as file:
        ubas_data = json.load(file)

    for uba_data in ubas_data:
        await create_uba(pool_, uba_data)

    print("UBAs criados:\n")
    for item in UBAs:
        print(f"{item}\n")

    #FARDINHOS -----------------------------------------------------------------------------------

    with open('fardinhos.json', 'r') as file:
        fardinhos_data = json.load(file)

    for fardinho_data in fardinhos_data:
        await create_fardinho(pool_, fardinho_data)

    print("Fardinhos criados:\n")
    for item in Fardinhos:
        print(f"{item}\n")

    #FCLIENTES -----------------------------------------------------------------------------------

    with open('clientes.json', 'r') as file:
        clientes_data = json.load(file)

    for cliente_data in clientes_data:
        await create_cliente(pool_, cliente_data)

    print("Clientes do mercado externo criados:\n")
    for item in Clientes:
        print(f"{item}\n")

    end_time = time.time()

    total_time = end_time - start_time
    print(f"Tempo total do codigo: {total_time} segundos")

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
