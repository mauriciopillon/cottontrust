import asyncio
import json
import time
import random
from indy import pool, wallet, did, ledger
from indy.error import ErrorCode, IndyError

UBAs = []
Fardinhos = []
Clientes = []

cont_Uba = 0
cont_Far = 0
cont_Cli = 0


async def setup_identity(identity, trustee):
    print('cheguei no setup identity')
    did_safe = 'V4SGRU86Z58d6TV7PBUe6f'
    verkey_safe = '~CoRER63DVYnWZtK8uAzNbx'
    (identity['did'], identity['key']) = await did.create_and_store_my_did(identity['wallet'], "{}")
    nym_req = await ledger.build_nym_request(did_safe, identity['did'],identity['key'],None, None)
    await ledger.sign_and_submit_request(identity['pool'], trustee['wallet'], did_safe, nym_req)
    
    
async def create_wallet(Entidade):
    print("\"{}\" -> Criando Carteira(wallet)".format(Entidade['name']))
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
        "balance": cliente_data['balance']
    }

    await create_wallet(CLIENTE)
    CLIENTE["did_info"] = json.dumps({'seed': CLIENTE['seed']})
    CLIENTE['did'], CLIENTE['key'] = await did.create_and_store_my_did(CLIENTE['wallet'], CLIENTE['did_info']) 

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
        "balance": uba_data['balance']
    }

    
    await create_wallet(UBA)

    UBA["did_info"] = json.dumps({'seed': UBA['seed']})
    UBA['did'], UBA['key'] = await did.create_and_store_my_did(UBA['wallet'], UBA['did_info'])

    # AQUI EH A FUNCAO DE SUBMETER PARA O LEDGER
    await setup_identity(UBA, trustee)
    UBAs.append(UBA)
    
async def create_transaction(sender, receiver, amount):
    # Verifique se o remetente tem saldo suficiente
    if sender['balance'] < amount:
        print(f"{sender['name']} nao tem saldo suficiente para a transacao")
        return

    # Atualize o saldo do remetente
    sender['balance'] -= amount

    # Construa a solicitação de atributo para o remetente
    sender_attr_req = await ledger.build_attrib_request(sender['did'], sender['did'], None, json.dumps({'balance': sender['balance']}), None)

    # Assine e envie a solicitação de atributo para o remetente
    await ledger.sign_and_submit_request(sender['pool'], sender['wallet'], sender['did'], sender_attr_req)

    # Atualize o saldo do destinatário
    receiver['balance'] += amount

    # Construa a solicitação de atributo para o destinatário
    receiver_attr_req = await ledger.build_attrib_request(receiver['did'], receiver['did'], None, json.dumps({'balance': receiver['balance']}), None)

    # Assine e envie a solicitação de atributo para o destinatário
    await ledger.sign_and_submit_request(receiver['pool'], receiver['wallet'], receiver['did'], receiver_attr_req)

    print(f"Transacao concluida: {sender['name']} enviou R${amount},00 para {receiver['name']}")

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

    with open('teste.json', 'r') as file
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
            await create_uba(pool_, uba_data, trustee)
        

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
            await create_cliente(pool_, cliente_data)

        print("Clientes do mercado externo criados:\n")
        for item in Clientes:
            print(f"{item}\n")

    # FIM -----------------------------------------------------------------------------------------

    if UBAs and Clientes:
        num_transacoes = 10  # Quantidade de transações

        for _ in range(num_transacoes):
            sender_uba = random.choice(UBAs)
            receiver_cliente = random.choice(Clientes)

            amount = random.randint(200, 1000)
            await asyncio.sleep(10)  # Adiciona uma pausa para garantir que o pool esteja aberto
            await create_transaction(sender_uba, receiver_cliente, amount)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
