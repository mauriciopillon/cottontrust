import asyncio
import json
import time
import csv
import random
import os

from indy_ndr import pool, wallet, did, ledger
from indy_ndr.error import ErrorCode, IndyError

from identity import setup_identity
from wallet import create_wallet, create_seed
from cliente import create_cliente
from fardinho import create_fardinho
from uba import create_uba
from transaction import create_transaction

UBAs = []
Fardinhos = []
Clientes = []

tempos_transacao = []
tempo_criacao = []

cont_Uba = 0
cont_Far = 0
cont_Cli = 0
cont_Tran = 0  

async def run():

    pool_ = {
        'name': 'pool1'
    }

    print("Open Pool Ledger: {}".format(pool_['name']))

    pool_['genesis_txn_path'] = "/home/indy/sandbox/cottontrust/genesis.txn"
    pool_['config'] = json.dumps({"genesis_txn": str(pool_['genesis_txn_path'])})

    await pool.set_protocol_version(2)

    try:
        await pool.create_pool_ledger_config(pool_['name'], pool_['config'])
    except IndyError as ex:
        if ex.error_code == ErrorCode.PoolLedgerConfigAlreadyExistsError:
            pass
    pool_['handle'] = await pool.open_pool_ledger(pool_['name'], None)


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

    # CRIANDO O TRUSTEE CONFIA EM DEUS E VAI
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
