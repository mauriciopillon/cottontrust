import asyncio
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


cont_Uba = 0
cont_Bale = 0
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
        'UBA registry code': uba_data['UBA registry code'],
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
            print("UBA file empty.\n")
            ubas_data = []

    if ubas_data:
        for uba_data in ubas_data:
            time_uba = time.time()
            await create_uba(pool_, uba_data, trustee)
            endtime_uba = time.time()
            time_create.append(endtime_uba - time_uba)

        print("UBAs created:\n")
        for item in UBAs:
            print(f"{item}\n")

    # BALES -----------------------------------------------------------------------------------

    with open('models/fardinhos.json', 'r') as file:
        try:
            bale_data = json.load(file)
        except json.JSONDecodeError:
            print("Bale file is empty.\n")
            bale_data = []

    if bale_data:
        for bale_data in bale_data:
            await create_bale(pool_, bale_data)

        print("Created bales:\n")
        for item in Bale:
            print(f"{item}\n")

    # CLIENTS -----------------------------------------------------------------------------------

    with open('models/clientes.json', 'r') as file:
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

        print("Clients created:\n")
        for item in Clients:
            print(f"{item}\n")

    # TRANSACTION -----------------------------------------------------------------------------------------

    if UBAs and Clients:
        num_trans = 4 # Quantidade de transações

        for _ in range(num_trans):

            sender= random.choice(Clients)
            receiver = random.choice(UBAs)
            bale_cost = receiver['bale_price']
            quant_bale = sender['req_bale']
            
            await create_transaction(sender, receiver, bale_cost, quant_bale)

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
