from indy_vdr.bindings import Pool, Wallet, Did

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

    CLIENTE['wallet'] = await Wallet.create(CLIENTE['wallet_config'], CLIENTE['wallet_credentials'])
    CLIENTE["did_info"] = json.dumps({'seed': CLIENTE['seed']})

    CLIENTE['did'], CLIENTE['key'] = await Did.create_and_store_my_did(CLIENTE['wallet'], CLIENTE['did_info']) 
    # AQUI EH A FUNCAO DE SUBMETER PARA O LEDGER
    await setup_identity(CLIENTE, trustee)
    Clientes.append(CLIENTE) 