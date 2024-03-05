from indy_vdr.bindings import Wallet, Did

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

    FARDINHO['wallet'] = await Wallet.create(FARDINHO['wallet_config'], FARDINHO['wallet_credentials'])
    FARDINHO["did_info"] = json.dumps({'seed': FARDINHO['seed']})

    FARDINHO['did'], FARDINHO['key'] = await Did.create_and_store_my_did(FARDINHO['wallet'], FARDINHO['did_info'])

    Fardinhos.append(FARDINHO) 