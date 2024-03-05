from indy_vdr.bindings import Pool, Wallet, Did

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

    # Create wallet using indy-vdr
    UBA['wallet'] = await Wallet.create(UBA['wallet_config'], UBA['wallet_credentials'])

    UBA["did_info"] = json.dumps({'seed': UBA['seed']})
    UBA['did'], UBA['key'] = await Did.create_and_store_my_did(UBA['wallet'], UBA['did_info'])

    # AQUI EH A FUNCAO DE SUBMETER PARA O LEDGER
    await setup_identity(UBA, trustee)
    UBAs.append(UBA)