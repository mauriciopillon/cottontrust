import asyncio
import json
import time
import csv
import random
import os
from indy import pool, wallet, did, ledger
from indy.error import ErrorCode, IndyError

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
    did_safe = 'V4SGRU86Z58d6TV7PBUe6f'
    verkey_safe = '~CoRER63DVYnWZtK8uAzNbx'
    (identity['did'], identity['key']) = await did.create_and_store_my_did(identity['wallet'], "{}")
    nym_req = await ledger.build_nym_request(did_safe, identity['did'],identity['key'],None, None)
    await ledger.sign_and_submit_request(identity['pool'], trustee['wallet'], did_safe, nym_req)
      
async def create_wallet(Entity):
    print("\"{}\" -> Creating  wallet(wallet)".format(Entity['name']))

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
    
def create_seed(contador, nome):
        seed =  str(nome) + str(contador) + 'A0000000000000000000000000000000000' 
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
        'Endereco - Pais': cliente_data['Endereco - Pais'],
        'wallet_config': json.dumps({'id': cliente_data['wallet_config']}),
        'wallet_credentials': json.dumps({'key': cliente_data['wallet_credentials']}),
        'pool': pool_['handle'],

        'seed': create_seed(cont_Cli, cliente_data['name']),
        "balance": cliente_data['balance'],
        "quero_fardinho": cliente_data['quero_fardinho'],
        "quant_fardinho": cliente_data['quant_fardinho']

    }

    await create_wallet(CLIENTE)
    CLIENTE["did_info"] = json.dumps({'seed': CLIENTE['seed']})

    CLIENTE['did'], CLIENTE['key'] = await did.create_and_store_my_did(CLIENTE['wallet'], CLIENTE['did_info']) 
    # AQUI EH A FUNCAO DE SUBMETER PARA O LEDGER
    await setup_identity(CLIENTE, trustee)
    Clientes.append(CLIENTE)  
    

async def create_fardinho(pool_, fardinho_data):
    global cont_Far
    cont_Far += 1
    

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

        'seed': create_seed(cont_Far, fardinho_data['name']),
        "balance": 1000

    }

    await create_wallet(FARDINHO)
    FARDINHO["did_info"] = json.dumps({'seed': FARDINHO['seed']})
    FARDINHO['did'], FARDINHO['key'] = await did.create_and_store_my_did(FARDINHO['wallet'], FARDINHO['did_info'])

    Fardinhos.append(FARDINHO) 

async def create_uba(pool_, uba_data, trustee):
    global cont_Uba
    cont_Uba += 1
    

    print(f"\nCriando UBA {cont_Uba} - Cadastre")
    


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

        'seed': create_seed(cont_Uba, uba_data['name']),
        "balance": uba_data['balance'],
        "preco_fardinho": uba_data['preco_fardinho'],#add
        "quant_fardinho": uba_data['quant_fardinho'] #add
    }

    
    await create_wallet(UBA)

    UBA["did_info"] = json.dumps({'seed': UBA['seed']})
    UBA['did'], UBA['key'] = await did.create_and_store_my_did(UBA['wallet'], UBA['did_info'])

    # AQUI EH A FUNCAO DE SUBMETER PARA O LEDGER
    await setup_identity(UBA, trustee)
    UBAs.append(UBA)
    
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

    # Construa a solicitação de atributo para o remetente
    sender_attr_req = await ledger.build_attrib_request(sender['did'], sender['did'], None, json.dumps({'balance': sender['balance'], 'quant_fardinho': sender['quant_fardinho']}), None)

    # Assine e envie a solicitação de atributo para o remetente
    await ledger.sign_and_submit_request(sender['pool'], sender['wallet'], sender['did'], sender_attr_req)

    # Atualize o saldo do destinatário
    receiver['balance'] += amount

    # Atualize a quantidade de Fardinhos do destinatário
    receiver['quant_fardinho'] -= quant_far

    # Construa a solicitação de atributo para o destinatário
    receiver_attr_req = await ledger.build_attrib_request(receiver['did'], receiver['did'], None, json.dumps({'balance': receiver['balance'], 'quant_fardinho': receiver['quant_fardinho']}), None)

    # Assine e envie a solicitação de atributo para o destinatário
    await ledger.sign_and_submit_request(receiver['pool'], receiver['wallet'], receiver['did'], receiver_attr_req)

    end_time = time.time()
    duration = end_time - start_time
    print(f"\nA transacao levou {duration} segundos para ser concluida\n")
    tempos_transacao.append(duration)

    print(f"Transacao concluida: {sender['name']} enviou R${amount},00 para {receiver['name']} e recebeu {quant_far} Fardinhos")
    print(f"Saldo atual de {sender['name']}: R${sender['balance']},00 e {sender['quant_fardinho']} Fardinhos")
    print(f"Saldo atual de {receiver['name']}: R${receiver['balance']},00 e {receiver['quant_fardinho']} Fardinhos")
    print("--------------------------------------------")

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


    with open('models/teste.json', 'r') as file:
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

    with open('models/ubas.json', 'r') as file:
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

    with open('models/fardinhos.json', 'r') as file:
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

    with open('models/clientes.json', 'r') as file:
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
            writer.writerow(["Quant. De Entitys:", "Tempo de Transacao:", "Tempo de Criacao:"])  # Escrever cabeçalho
        for t, tc in zip(tempos_transacao, tempo_criacao):
            writer.writerow(["100", t, tc])  # Escrever dados
        writer.writerow([])
print("Concluído.")

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
